import requests

url = "https://stock.xueqiu.com/v5/stock/quote.json"
params = {
    "symbol": "SZ300750",
    "extend": "detail",
}

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0"
    ),
    # 如果你有浏览器里复制的 Cookie，可以贴到下面这一行
    "Cookie": "xq_a_token=9492bad942dadf90b60f270aac7d5b5e982fdf82; xqat=9492bad942dadf90b60f270aac7d5b5e982fdf82; xq_r_token=edf6f46eaceb40d684979451929ef3d7c0928034; xq_id_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1aWQiOi0xLCJpc3MiOiJ1YyIsImV4cCI6MTc2Njc5ODE1MSwiY3RtIjoxNzY0ODQyNjU3NzY5LCJjaWQiOiJkOWQwbjRBWnVwIn0.iYRTiPGm73jTMkeJNdksIHrxMdTj4ETP81IA2dF80nodjTumV8WXO4D99pkXNyOOGzw9XTLT6LS5BvfSwo16R4INPlJZJXJnQ7tughLcRxPK-0FoaCL6ZHQYFpi10xdbpSJRl3PMZKUBfl87BzYyD7oGvrEewY3aY1d_qEv4xOHEj70wqecpUfw7jwItjb4o8RVoh7R9ZAgnALRfwcG7yGeH2jTbN0RVUvHsgEeSde1fPd2zWnKR9vGeUfn_xBs-dCYpD6yXwBQBuBcjd67iIquAYjsRcCY2NbjRhDut80N8xG5xwEgN7OX1amGEx_3vozWeO4O_75W3zXNeQDQ1Bw; cookiesu=931764842715080; u=931764842715080; device_id=26e0857e322721bc0304e452a0807a35; Hm_lvt_1db88642e346389874251b5a1eded6e3=1764842720; HMACCOUNT=38D66FD954EA0CCF; s=a511lm96bq; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1764843385; is_overseas=0; ssxmod_itna=1-CqGxuQG=KYqWwxeKYKitriODCDm2D_pGaxBP017sDu2xjKidQDU7YNg0rtEDiTPue=8Ci7GqbqnxGXkmDA5Dnzx7YDtrSPN=enpAGwkT7R7ipoS/rGoh63L7iwk63aL94qMj6vz1qSnoh5bDB3DbqDy8Ge=YxGGf4GwDGoD34DiDDpfD03Db4D_SjrD72btxaWdheqDQ4GyDitDKqqaxG3D0RRobGAQoDDlY774IGauDYPdVji72iFDAuGNv74dx0taDBd5nIDdxDU6MIGbVCSfrFoY1caDtqD9f6uqpaIQN=nKrIeKBroVr4U0DKgDI7GGWxzCGeYYdBG3WheBX3mm5GDeA0xBixfwt4DASYHB4NBPo7yMmvpAvZFeFeT1/qHDTrK9DIDHtut8BN4_K8YeYxepYNK0q7i5OiPeD; ssxmod_itna2=1-CqGxuQG=KYqWwxeKYKitriODCDm2D_pGaxBP017sDu2xjKidQDU7YNg0rtEDiTPue=8Ci7GqbqYxD3beYcloWvtvALyXG8b0q_WXeeD",
    "Referer": "https://xueqiu.com/",
}

def test_xueqiu_api():
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        print("Status code:", resp.status_code)

        # 打印部分响应头
        print("Response headers:")
        for k, v in resp.headers.items():
            print(f"  {k}: {v}")

        print("\nRaw text response:")
        print(resp.text[:1000])  # 只打印前 1000 字符，避免太长

        # 尝试解析成 JSON
        try:
            data = resp.json()
            print("\nParsed JSON keys:", list(data.keys()))
            print("\nFull JSON:")
            print(data)
        except ValueError:
            print("\nResponse is not valid JSON.")
    except Exception as e:
        print("Request error:", e)

if __name__ == "__main__":
    test_xueqiu_api()
