import ccxt
import time
from tqdm import tqdm

# Configurarea API-ului
api_key = 'XXX'
api_secret = 'XXX'

# Inițializarea exchange-ului (Binance folosit ca exemplu)
exchange = ccxt.binance({
    'apiKey': api_key,
    'secret': api_secret
})

# Culori pentru mesaje
COLOR_GREEN = "\033[92m"
COLOR_RED = "\033[91m"
COLOR_ORANGE = "\033[93m"
COLOR_RESET = "\033[0m"
COLOR_CYAN = "\033[96m"


def print_colored(message, color):
    """Afișează un mesaj colorat."""
    print(f"{color}{message}{COLOR_RESET}")  # Adăugăm \n pentru claritate


def progress_bar_with_tqdm(duration):
    """Afișează o bară de progres utilizând tqdm."""
    for _ in tqdm(range(duration), desc="Așteptare", ncols=80, bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} secunde"):
        time.sleep(1)
#    print("\n")  # Linie nouă după finalizarea barei


def get_wallet_balances():
    """Obține balanțele din portofel."""
    balances = exchange.fetch_balance()
    if 'total' not in balances or not isinstance(balances['total'], dict):
        print_colored("Structura balanțelor este incorectă.", COLOR_RED)
        return {}
    return {coin: amount for coin, amount in balances['total'].items() if amount > 0}


def get_prices():
    """Obține prețurile curente pentru toate perechile."""
    tickers = exchange.fetch_tickers()
    if not isinstance(tickers, dict):
        print_colored("Structura tickers este incorectă.", COLOR_RED)
        return {}
    return {pair: ticker['last'] for pair, ticker in tickers.items() if 'last' in ticker}


def find_highest_value_coin(wallet_balances, prices):
    """Găsește moneda cu cea mai mare valoare în $, inclusiv USDT."""
    usdt_balance = wallet_balances.get('USDT', 0)
    values = {'USDT': usdt_balance}  # Include USDT în lista monedelor
    for coin, balance in wallet_balances.items():
        if coin == 'USDT':  # Sari peste USDT, deja inclus
            continue
        pair = f'{coin}/USDT'
        price = prices.get(pair, 0)
        values[coin] = balance * price
    if not values:
        return 'USDT', usdt_balance
    return max(values, key=values.get), max(values.values())


def find_best_coin_to_buy(prices, excluded_coins):
    """Găsește moneda cu cea mai mare creștere procentuală, excluzând monedele deja deținute."""
    growth = {}
    tickers = exchange.fetch_tickers()
    for pair, ticker in tickers.items():
        if 'percentage' in ticker and ticker['percentage'] is not None:
            coin = pair.split('/')[0]
            if '/USDT' in pair and coin not in excluded_coins:
                growth[pair] = ticker['percentage']
    sorted_growth = sorted(growth.items(), key=lambda x: x[1], reverse=True)
    return [pair.split('/')[0] for pair, _ in sorted_growth]


def convert_to_new_coin(current_coin, target_coin, balance):
    """
    Convertește balanța din moneda curentă în altă monedă.
    Folosește USDT sau altă monedă dominantă.
    """
    try:
        # Dacă deja avem USDT, cumpără direct target_coin
        if current_coin == 'USDT':
            usdt_pair_buy = f'{target_coin}/USDT'
            if usdt_pair_buy in exchange.symbols:
                price_buy = exchange.fetch_ticker(usdt_pair_buy)['last']
                target_amount = balance / price_buy
                if target_amount < 10e-8:  # Verifică dacă valoarea este mai mică decât minimul permis
                    print_colored(f"Balanța USDT insuficientă pentru a cumpăra {target_coin}.", COLOR_RED)
                    return False
                exchange.create_market_buy_order(usdt_pair_buy, target_amount)
                print_colored(f"Conversie reușită: Cumpărat {target_amount:.6f} {target_coin} folosind USDT.", COLOR_ORANGE)
                return True  # Finalizează cu succes
            else:
                print_colored(f"Perechea {usdt_pair_buy} nu este disponibilă.", COLOR_RED)
                return False

        # Vinde moneda curentă pentru USDT
        usdt_pair_sell = f'{current_coin}/USDT'
        if usdt_pair_sell in exchange.symbols:
            price_sell = exchange.fetch_ticker(usdt_pair_sell)['last']
            usdt_amount = balance * price_sell * 0.999
            exchange.create_market_sell_order(usdt_pair_sell, balance)
            print_colored(f"Conversie reușită: Vândut {balance:.6f} {current_coin} pentru USDT.", COLOR_ORANGE)
            return usdt_amount  # Returnează balanța actualizată în USDT
        else:
            print_colored(f"Perechea {current_coin}/USDT nu este disponibilă.", COLOR_RED)
            return 0
    except Exception as e:
        print_colored(f"Eroare la conversia monedei {current_coin} în {target_coin}: {e}", COLOR_RED)
        return 0


def monitor_wallet():
    """Monitorizează periodic portofelul."""
    last_coin = None  # Ultima monedă verificată
    last_value = None  # Ultima valoare cunoscută a monedei dominante

    while True:
        wallet_balances = get_wallet_balances()
        if not wallet_balances:
            print_colored("Nu există balanțe disponibile.", COLOR_RED)
            time.sleep(10)
            continue

        prices = get_prices()
        if not prices:
            print_colored("Nu s-au putut obține prețurile.", COLOR_RED)
            time.sleep(10)
            continue

        # Determină moneda dominantă
        top_coin, top_value = find_highest_value_coin(wallet_balances, prices)
        if not top_coin:
            print_colored("Nu s-a putut determina moneda dominantă.", COLOR_RED)
            time.sleep(10)
            continue

        # Dacă moneda s-a schimbat, resetează comparația
        if last_coin != top_coin:
            last_coin = top_coin
            last_value = top_value

        print_colored(f"Moneda dominantă: {top_coin}, Valoare în $: {top_value:.2f}", COLOR_CYAN)

        # Dacă moneda dominantă este USDT, cumpără direct o monedă promițătoare
        if top_coin == 'USDT':
            print_colored("USDT este moneda dominantă. Cumpăr o monedă promițătoare...", COLOR_GREEN)
            best_coins = find_best_coin_to_buy(prices, excluded_coins=list(wallet_balances.keys()))
            success = False
            for new_coin in best_coins:
                try:
                    if convert_to_new_coin('USDT', new_coin, wallet_balances['USDT']):
                        success = True
                        break
                except Exception as e:
                    print_colored(f"Nu am putut cumpăra {new_coin} folosind USDT: {e}", COLOR_RED)
            if not success:
                print_colored("Toate încercările de cumpărare au eșuat. Aștept 20 de minute înainte de a reîncerca.", COLOR_RED)
                progress_bar_with_tqdm(300)
            continue

        # Compară valoarea curentă cu ultima valoare
        if top_value < last_value:
            print_colored(f"Valoarea a scăzut de la {last_value:.2f} la {top_value:.2f}. Căutăm o altă monedă pentru cumpărare...", COLOR_RED)

            # Exclude moneda dominantă din lista de cumpărare
            best_coins = find_best_coin_to_buy(prices, excluded_coins=list(wallet_balances.keys()))
            for new_coin in best_coins:
                try:
                    usdt_balance = convert_to_new_coin(top_coin, new_coin, wallet_balances[top_coin])
                    if usdt_balance:  # Dacă conversia este făcută, cumpără direct
                        print_colored("Conversia către USDT a avut loc. Cumpărăm o nouă monedă promițătoare imediat.", COLOR_GREEN)
                        for buy_coin in find_best_coin_to_buy(prices, excluded_coins=list(wallet_balances.keys())):
                            if convert_to_new_coin('USDT', buy_coin, usdt_balance):
                                break
                        progress_bar_with_tqdm(300)
                        break
                except Exception as e:
                    print_colored(f"Nu am putut converti {top_coin} în {new_coin}: {e}", COLOR_RED)
        else:
            print_colored("Valoarea este stabilă sau a crescut.", COLOR_GREEN)
            # Așteaptă 20 minute cu bara de progres utilizând tqdm
            progress_bar_with_tqdm(300)

        last_value = top_value


if __name__ == "__main__":
    try:
        monitor_wallet()
    except Exception as e:
        print_colored(f"Eroare: {e}", COLOR_RED)
