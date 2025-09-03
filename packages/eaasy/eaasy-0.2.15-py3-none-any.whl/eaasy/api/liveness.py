from flask_restx import Namespace, Resource

liveness_ns = Namespace("Liveness", description="Liveness", path="/liveness")

@liveness_ns.route('')
class Liveness(Resource): # pragma: no cover
    def get(self):
        '''Liveness'''

        return 'Ok', 200