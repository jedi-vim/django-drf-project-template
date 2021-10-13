from datetime import datetime

from rest_framework import generics
from rest_framework.exceptions import NotFound, ValidationError

from ecommerce_backend.reports.api.serializers import (
    CommisionSalesPersonSerializer,
    SellablePurchasedRankingSerializer,
)
from ecommerce_backend.reports.helpers import (
    sellables_acquired_ranked_by_quantity,
    total_comission_per_salesperson,
)


class CommisionPerSalespersonView(generics.RetrieveAPIView):
    serializer_class = CommisionSalesPersonSerializer

    def get_object(self):
        query_params = self.request.query_params
        if not query_params.get("salesperson_id"):
            raise ValidationError(
                detail={"salesperson_id": "Salesperson ID not provided"}
            )
        try:
            salesperson_id = int(query_params["salesperson_id"])
        except ValueError:
            raise ValidationError(
                detail={
                    "salesperson_id": f'{query_params["salesperson_id"]}'
                    " is a invalid ID"
                }
            )
        try:
            begin = datetime.strptime(query_params["begin"], "%Y-%m-%d %H:%M:%S")
            end = datetime.strptime(query_params["end"], "%Y-%m-%d %H:%M:%S")
        except ValueError:
            raise ValidationError(detail={"Invalid dates"})
        retval = total_comission_per_salesperson(salesperson_id, begin, end)
        if not retval.exists():
            raise NotFound(detail="Report not available")
        return retval[0]


class SellablePurchasedRankingView(generics.ListAPIView):
    serializer_class = SellablePurchasedRankingSerializer

    def get_queryset(self):
        query_params = self.request.query_params
        if query_params.get("customer_id"):
            try:
                customer_id = int(query_params.get("customer_id"))
            except ValueError:
                raise ValidationError(
                    detail={
                        "customer_id": f'{query_params["customer_id"]}'
                        " is a invalid ID"
                    }
                )
        else:
            customer_id = None

        try:
            begin = datetime.strptime(query_params["begin"], "%Y-%m-%d %H:%M:%S")
            end = datetime.strptime(query_params["end"], "%Y-%m-%d %H:%M:%S")
        except ValueError:
            raise ValidationError(detail={"Invalid dates"})

        retval = sellables_acquired_ranked_by_quantity(begin, end, customer_id)
        if not retval.exists():
            raise NotFound(detail="Report not available")
        return retval
