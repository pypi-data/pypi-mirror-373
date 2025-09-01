from example.api.grpc.health import v1


class HealthServer(v1.HealthBase):
    async def check(
        self, health_check_request: v1.HealthCheckRequest
    ) -> v1.HealthCheckResponse:
        return v1.HealthCheckResponse(
            status=v1.HealthCheckResponseServingStatus.SERVING
        )
