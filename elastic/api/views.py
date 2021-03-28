import tempfile
from datetime import timedelta
from urllib.parse import urlencode

import jwt
import requests as requester
from django.core import files
from django.db.models import Q
from django.utils import timezone
from google.auth.transport import requests
from google.oauth2 import id_token
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.settings import api_settings

from elastic.api.models import User
from elastic.api.serializers import UserRegisterSerializer
from elastic.elastic.settings import FIREBASE_ANDROID_APP_ID, FIREBASE_IOS_APP_ID, AUTH_APPLE_KEY_ID, \
    AUTH_APPLE_TEAM_ID, AUTH_APPLE_CLIENT_ID, AUTH_APPLE_PRIVATE_KEY, ACCESS_TOKEN_URL


class GoogleView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        token = {'id_token': request.data.get('id_token')}
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        try:
            idinfo = id_token.verify_token(token['id_token'], requests.Request())
            if idinfo['aud'] not in [FIREBASE_ANDROID_APP_ID, FIREBASE_IOS_APP_ID]:
                raise ValueError('Could not verify audience.')

            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')

            if User.objects.filter(Q(email=idinfo['email']) | Q(username=idinfo['email'])).exists():
                user = User.objects.get(email=idinfo['email'])
            else:
                password = User.objects.make_random_password()
                user = User.objects.create_user(email=idinfo['email'], username=idinfo['email'],
                                                first_name=idinfo['given_name'],
                                                last_name=idinfo['family_name'],
                                                password=password)
                name = idinfo['email'].replace('@', '_').replace('.', '_') + '.png'
                response = requester.get(idinfo['picture'], stream=True)
                if response.status_code != requester.codes.ok:
                    lf = tempfile.NamedTemporaryFile()
                    for block in response.iter_content(1024 * 8):
                        if not block:
                            break
                        lf.write(block)
                    user.image.save(name, files.File(lf))

            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)
            serializer = UserRegisterSerializer(user)
            return Response({'token': token, 'user': serializer.data})
        except ValueError as err:
            # Invalid token
            content = {'message': err.__str__()}
            return Response(content, 500)


class AppleView(APIView):
    permission_classes = (AllowAny,)

    def get_key_and_secret(self):
        headers = {
            'kid': AUTH_APPLE_KEY_ID,
            'alg': 'ES256'
        }
        payload = {
            'iss': AUTH_APPLE_TEAM_ID,
            'iat': timezone.now(),
            'exp': timezone.now() + timedelta(days=180),
            'aud': 'https://appleid.apple.com',
            'sub': AUTH_APPLE_CLIENT_ID,
        }
        client_secret = jwt.api_jwt.encode(
            payload,
            AUTH_APPLE_PRIVATE_KEY,
            algorithm="ES256",
            headers=headers
        )
        return AUTH_APPLE_CLIENT_ID, client_secret

    def post(self, request):
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        if request.Android and not request.data.get('access_token'):
            vars = urlencode(request.data, doseq=False)
            redirect_url = 'intent://callback?' + vars + '#Intent;package=engineering.aleph.flexsports' \
                                                         ';scheme=signinwithapple;end'
            response = Response('', 302)
            response['Location'] = redirect_url
            return response

        access_token = request.data.get('access_token')
        refresh_token = request.data.get('refresh_token')
        client_id, client_secret = self.get_key_and_secret()
        headers = {'content-type': "application/x-www-form-urlencoded"}
        data = {
            'client_id': client_id,
            'client_secret': client_secret,
        }
        if refresh_token is None:
            data['code'] = access_token
            data['grant_type'] = 'authorization_code'
        else:
            data['refresh_token'] = refresh_token
            data['grant_type'] = 'refresh_token'
        #
        res = requester.post(ACCESS_TOKEN_URL, data=data, headers=headers)
        response_dict = res.json()
        if 'error' not in response_dict:
            id_token = response_dict.get('id_token', None)
            refresh_tk = response_dict.get('refresh_token', None)
            decoded = jwt.decode(id_token, '', verify=False) if id_token else None
            if id_token and decoded:
                try:
                    if User.objects.filter(Q(email=decoded['email']) | Q(username=decoded['email'])).exists():
                        user = User.objects.get(email=decoded['email'])
                    else:
                        name = decoded['email'].split('@')[0]
                        user = User.objects.create_user(email=decoded['email'], username=decoded['email'],
                                                        first_name=name,
                                                        last_name=name,
                                                        password=User.objects.make_random_password())

                    payload = jwt_payload_handler(user)
                    token = jwt_encode_handler(payload)
                    serializer = UserRegisterSerializer(user)
                    data = {'token': token, 'user': serializer.data}
                    if refresh_tk is not None:
                        data['refresh_token'] = refresh_tk
                    return Response(data)
                except AssertionError as err:
                    # Invalid token
                    content = {'message': err.__str__()}
                    return Response(content, 500)
        else:
            content = {'message': response_dict.__str__()}
            return Response(content, 500)