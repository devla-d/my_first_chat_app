from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from app.serializers import RegistrationSerializer,ProfileSerializer,FriendsSerializers
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from app.models import Account,Friend,RoomMember,Room,Message
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView











@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
	user = request.user
	print(user)
	#user = get_object_or_404(Account, pk=1)
	serializer = ProfileSerializer(user)
	return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def friends(request):
	user = request.user
	print(user)
	user = get_object_or_404(Friend, user=user)
	serializer = FriendsSerializers(user)
	return Response(serializer.data)





@api_view(['GET'])
@permission_classes([IsAuthenticated])
def users(request):
	user = request.user
	my_friends = get_object_or_404(Friend, user=user)
	queryset = Account.objects.all()
	#queryset  = []
	'''for qs in obj_queryset:
		for my in my_friends.friends.all():
			if qs.username != my.username:
				queryset.append(qs)'''
	serializer = ProfileSerializer(queryset, many=True)
	return Response(serializer.data)

 



class AddFriendView(APIView):

	#authentication_classes = []
	permission_classes = [IsAuthenticated]

	def post(self, request):
		context = {}
		user = request.user
		print(user)
		pk = int(request.POST.get('pk'))
		new_friend = get_object_or_404(Account, pk=pk)
		user_friend = get_object_or_404(Friend, user=user)
		user_friend.friends.add(new_friend)
		new_friend_add =  get_object_or_404(Friend, user=new_friend)
		new_friend_add.friends.add(user)
		our_room = Room.objects.create(owner=user,friend=new_friend)
		RoomMember.objects.create(room=our_room,user=new_friend)
		context['res'] = 'Successfully'
		context['pk'] = new_friend.pk
		return Response(context)


class ChatView(APIView):

	#authentication_classes = []
	#permission_classes = [IsAuthenticated]

	def get(self, request, *args, **kwargs):
		"""return all messages in a chat session."""
		'''user = request.user
		chat_friend = request.data['Chat_friend_id']'''
		uri = kwargs['uri']
		room = get_object_or_404(Room,uri=uri)
		messages = [chat_session_message.to_json() 
		for chat_session_message in room.messages.all()]

		return Response({
		'id': room.id, 'uri': room.uri,
		'messages': messages
		})
	
	def post(self, request, *args, **kwargs):
		context = {}
		user = request.user
		friend_pk = request.POST.get('friend_pk')
		friend = get_object_or_404(Account,pk=friend_pk)
		try:
			room = Room.objects.get(owner=user,friend=friend)
		except:
			room = Room.objects.get(owner=friend,friend=user)
		if room:
			print(room.uri)
			context['room'] = room.uri
			return Response(context)





@api_view(['POST',])
def registration_view(request):

	if request.method == 'POST':
		data = {}
		email = request.data.get('email', '0').lower()
		if validate_email(email) != None:
			data['error_message'] = 'That email is already in use'
			data['response'] = 'Error'
			return Response(data)

		username = request.data.get('username', '0')
		if validate_username(username) != None:
			data['error_message_username'] = 'That username is already in use'
			data['response'] = 'Error'
			return Response(data)

		serializer = RegistrationSerializer(data=request.data)
		
		if serializer.is_valid():
			account = serializer.save()
			data['response'] = 'successfully registered new user.'
			data['email'] = account.email
			data['username'] = account.username
			data['pk'] = account.pk
			#token = Token.objects.get(user=account).key
			#data['token'] = token
		else:
			data = serializer.errors
		return Response(data)
	






def validate_email(email):
	account = None
	try:
		account = Account.objects.get(email=email)
	except Account.DoesNotExist:
		return None
	if account != None:
		return email

def validate_username(username):
	account = None
	try:
		account = Account.objects.get(username=username)
	except Account.DoesNotExist:
		return None
	if account != None:
		return username







class ObtainAuthTokenView(APIView):

	authentication_classes = []
	permission_classes = []

	def post(self, request):
		context = {}

		email = request.POST.get('username')
		password = request.POST.get('password')
		print('email=',email)
		account = authenticate(email=email, password=password)
		if account:
			try:
				token = Token.objects.get(user=account)
			except Token.DoesNotExist:
				token = Token.objects.create(user=account)
			context['res'] = 'Successfully authenticated.'
			context['pk'] = account.pk
			context['email'] = email.lower()
			context['username'] = account.username
			context['token'] = token.key
		else:
			context['response_error'] = 'Error'

		return Response(context)
