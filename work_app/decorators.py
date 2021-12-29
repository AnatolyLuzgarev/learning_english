from django.http import HttpResponse

def only_get_post(func):
	def get_post_func(request):
		if request.method == "GET" or request.method == "POST":
			return func(request)
		else:
			return HttpResponse(status = 501)
	return get_post_func
		
def only_get(func):
	def get_post_func(request):
		if request.method == "GET":
			return func(request)
		else:
			return HttpResponse(status = 501)
	return get_post_func