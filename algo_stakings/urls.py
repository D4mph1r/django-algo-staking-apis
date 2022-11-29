from algo_stakings import views
from django.urls import path


urlpatterns = [
    path("get-all-nfts", views.NftsView.as_view()),
    path("earned/<int:appId>/<str:address>",
         views.EarnedView.as_view()),
    path("get-all-stakings/<int:appId>/<str:address>",
         views.AllStakingsView.as_view()),
    path("get-nfts-status-by-address/<str:address>",
         views.NftsTransactionsView.as_view()),
    path("transfer-asset", views.TransferAsset.as_view())
]
