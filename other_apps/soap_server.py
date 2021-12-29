#SOAP Libraries######################################
from spyne import Application, rpc, ServiceBase, Unicode,Integer, Iterable
from spyne.protocol.soap import Soap11
from spyne.protocol.http import HttpRpc
from spyne.server.wsgi import WsgiApplication
####################################################



#SOAP classes and methods
	
class GetDegree(ServiceBase):
	@rpc(Integer,Integer, _returns = Integer)
	def get_degree(ctx,number,degree):
		return number


application = Application([GetDegree],
    tns='spyne.examples.my_soap_server',
    in_protocol=HttpRpc(validator='soft'),
    # in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11()
)
application = WsgiApplication(application)


              
#Launching SOAP server on port 8001
if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    server = make_server('0.0.0.0', 8005, application)
    server.serve_forever()





