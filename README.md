# **🚀 CryptoBot**

### **🤖 Automated Trading Bot for Binance**

CryptoBot is an automated trading bot that interacts with the Binance exchange. It evaluates your wallet and performs trades based on predefined logic, aiming to optimize your holdings.

---

## **✨ Features**
- 🔑 Trades on Binance using your **API key** and **secret**.
- 💰 Automatically checks your wallet and identifies the **most dominant coin** in value.
- 📊 Trades from less favorable coins to **more promising ones** based on price trends.
- 🕒 Configurable **check interval** (default: every 5 minutes).
- 📝 Logs transactions and trading decisions in **real-time**.

---

## **🔧 Setup**

### **1. Configure API Key and Secret**
Edit the script and replace `XXX` with your Binance API key and secret:

```python
api_key = 'XXX'
api_secret = 'XXX'
```

### **2. Enable API Access on Binance**
1. 🔐 Log in to your Binance account.
2. Go to the **API Management** section.
3. Create a new API key and **enable the following permissions**:
   - **Read** (Required to fetch wallet balances and prices).
   - **Spot Trading** (Required to perform trades).
4. 🔒 **Whitelist your server's IP address** in the Binance API settings to ensure secure access.

---

## **📦 Installation**

Ensure you have Python 3 installed, then install the required dependencies:

```bash
pip install ccxt
pip install tqdm
```

---

## **🚀 Usage**

Run the bot with the following command:

```bash
python3 cryptobot.py
```

---

## **⚙️ Configuration**

### **🔄 Change the Check Interval**
By default, the bot checks your wallet every **5 minutes (300 seconds)**. To change this interval:
1. Open the script in your favorite text editor.
2. Search for `300` and replace it with your desired interval (in seconds).

---

## **📈 Example Output**

The bot logs its actions in real-time. Example:

```
Moneda dominantă: BTC, Valoare în $: 40,000
Valoarea este stabilă sau a crescut.
Așteptare: 100%|█████████████████████████████████████████████████| 300/300 secunde

Moneda dominantă: ETH, Valoare în $: 2,500
Valoarea a scăzut de la 40,000 la 2,500. Căutăm o altă monedă pentru cumpărare...
Conversie reușită: Vândut 0.1 BTC pentru USDT.
Conversie reușită: Cumpărat 1.2 ETH folosind USDT.
```

---

## **⚠️ Disclaimer**
CryptoBot is **not financial advice**. 🚨 **Trading cryptocurrencies involves significant risk** and can result in substantial losses. Use this bot at your own risk.

---

## **🎉 Enjoy Your Winnings... Or Not!**
Feel free to contribute or customize the script to suit your trading strategies. 😊

---

## **🌟 Contributions**
Contributions are welcome! If you encounter issues or have ideas for new features, feel free to open a pull request or an issue.
