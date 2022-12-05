from rest_framework import generics
from rest_framework.response import Response
from django.core import serializers
from algo_stakings import serializers, models, utils
# Create your views here.
from algosdk import mnemonic
from algosdk.future import transaction
import base64
from nftDjango.settings import MNEMONIC


class NftsView(generics.ListAPIView):
    serializer_class = serializers.nftsSerializer

    def get_queryset(self):
        all_nfts_transactions = models.NftsTransactions.objects.filter(
            isClaimed=True).values_list("assetId")
        return models.Nfts.objects.exclude(assetId__in=all_nfts_transactions)


class NftsTransactionsView(generics.ListAPIView):
    serializer_class = serializers.nftsTransactionsSerializer

    def get_queryset(self):
        query = models.NftsTransactions.objects.filter(
            address=self.kwargs["address"])
        return query


class EarnedView(generics.GenericAPIView):
    def get(self, *args, **kwargs):
        try:
            appId = kwargs["appId"]
            address = kwargs["address"]
            lockTime = 7890000
            algod_client = utils.getAlgodClient()
            latestBlock = algod_client.status()["last-round"]

            latestBlockTimeStamp = algod_client.block_info(latestBlock)[
                "block"]["ts"]
            print("latestBlockTimeStamp", latestBlockTimeStamp)

            accountApplicationInfo = algod_client.account_application_info(
                str(address), appId)
            print("accountApplicationInfo", accountApplicationInfo)

            for idx in range(9):
                state_key = idx.to_bytes(8, "big")
                state_key = base64.b64encode(
                    "stakings".encode('UTF-8')+state_key).decode("utf-8")
                try:
                    stored_staking = [x for x in accountApplicationInfo["app-local-state"]
                                      ["key-value"] if x["key"] == state_key][0]["value"]["bytes"]
                    state_decoded = utils.staking_codec.decode(
                        base64.b64decode(stored_staking))
                    lockTime = state_decoded[6]
                    break
                except Exception as e:
                    pass

            lastClaimTimeStampKey = base64.b64encode(
                bytes("dynamic_account_valuelcts", 'utf-8')).decode("utf-8")

            lastClaimTimeStamp = [x for x in accountApplicationInfo["app-local-state"]
                                  ["key-value"] if x["key"] == lastClaimTimeStampKey][0]["value"]["uint"]

            tokensStakedByAddressKey = base64.b64encode(
                bytes("dynamic_account_valuetsba", 'utf-8')).decode("utf-8")

            tokensStakedByAddress = [x for x in accountApplicationInfo["app-local-state"]
                                     ["key-value"] if x["key"] == tokensStakedByAddressKey][0]["value"]["uint"]

            reward = ((tokensStakedByAddress * utils.LOCKTIME[str(lockTime)] * (
                latestBlockTimeStamp - lastClaimTimeStamp))) / int(lockTime) / 100000000

            data = {
                "appId": appId,
                "earned": reward
            }
            return Response({"data": data})
        except Exception as e:
            return Response({"error": e})


class AllStakingsView(generics.ListAPIView):
    def get(self, *args, **kwargs):
        try:
            appId = kwargs["appId"]
            address = kwargs["address"]
            stakinglist = []
            algod_client = utils.getAlgodClient()
            accountApplicationInfo = algod_client.account_application_info(
                str(address), appId)
            for idx in range(9):
                state_key = idx.to_bytes(8, "big")
                state_key = base64.b64encode(
                    "stakings".encode('UTF-8')+state_key).decode("utf-8")
                try:
                    stored_staking = [x for x in accountApplicationInfo["app-local-state"]
                                      ["key-value"] if x["key"] == state_key][0]["value"]["bytes"]
                    state_decoded = utils.staking_codec.decode(
                        base64.b64decode(stored_staking))
                    txnId = models.NftsTransactions.objects.filter(address=str(address), appId=int(
                        appId), stakeId=int(state_decoded[1])).values_list("txId")[0][0]
                    txId = ""
                    if (txnId is not None):
                        txId = txnId
                    stakinglist.append(utils.stakings(appId, state_decoded[0], state_decoded[1], state_decoded[2],
                                                      state_decoded[3], state_decoded[4], state_decoded[5], state_decoded[6], txId))
                except Exception as e:
                    pass

            results = [obj.to_dict() for obj in stakinglist]
            return Response({"data": results})
        except Exception as e:
            return Response({"error": e})


class TransferAsset(generics.UpdateAPIView):
    def post(self, request, *args, **kwargs):
        try:
            assetId = request.data["assetId"]
            address = request.data["address"]
            nftsTransactionData = models.NftsTransactions.objects.filter(
                address=str(address), assetId=int(assetId), isClaimed=False).values()

            if (len(nftsTransactionData) > 0):
                algod_client = utils.getAlgodClient()
                sp = algod_client.suggested_params()
                sp.flat_fee = True
                sp.fee = 1_000

                adminMnemonic = MNEMONIC
                privateKey = mnemonic.to_private_key(adminMnemonic)
                adminAddress = mnemonic.to_public_key(adminMnemonic)

                assetTransferTxn = transaction.AssetTransferTxn(
                    sender=adminAddress, sp=sp, receiver=address, amt=1, index=assetId)

                print(adminMnemonic)
                sendTxn = algod_client.send_transaction(
                    assetTransferTxn.sign(privateKey))

                result = transaction.wait_for_confirmation(
                    algod_client, sendTxn, 4)

                nftsTransactionData[0]["isClaimed"] = True
                models.NftsTransactions.objects.filter(id=int(nftsTransactionData[0]["id"])).update(
                    isClaimed=nftsTransactionData[0]["isClaimed"])

                return Response({"data": result})

            else:
                data = {
                    "status": 404,
                    "message": "Bad Request or Already claimed"
                }

            return Response({"data": data})
        except Exception as e:
            print('ERROR', e)
            return Response(e)
