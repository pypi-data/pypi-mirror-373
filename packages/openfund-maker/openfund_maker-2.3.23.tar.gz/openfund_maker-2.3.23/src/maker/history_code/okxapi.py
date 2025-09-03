import okx.PublicData as PublicData

def fetch_and_store_all_instruments(instType='SWAP'):
    flag = "1"  # live trading: 0, demo trading: 1
    api_key = "55e6d01d-99ac-4790-b703-91f2bf9a8a36"
    secret_key = "13853744EA70BEB6B893E8993562AEF2"
    passphrase = "Openfund@100"
    
    PublicDataAPI = PublicData.PublicAPI(api_key, secret_key, passphrase, False, flag)

    result = PublicDataAPI.get_instruments(
    instType=instType
    )
    print(result)


def main():
    fetch_and_store_all_instruments()

if __name__ == '__main__':
    main()
