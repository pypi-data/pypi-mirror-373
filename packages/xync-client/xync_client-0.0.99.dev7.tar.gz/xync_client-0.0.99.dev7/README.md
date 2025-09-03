## Order Flow:
- 0: Получшение заявок за заданное время, в статусе, по валюте, монете, направлению: `get_orders(stauts=OrderStatus.active, coin='USDT', cur='RUB', is_sell=False) => [order]`

### Order Class description:
- 1: [T] Запрос на старт сделки (`order`) по чужому объявлению (`ad`) тейкером на сумму amount: `order_request(ad_id, amount) => order_id`
- 1N: [M] - Запрос мейкеру на сделку `order_request_ask => Order`
- 2: [T] Отмена запроса на сделку `cancel_request()`
- 2N: [M] - Уведомление об отмене запроса на сделку `request_canceled_notify`
- 3: [M] Одобрить запрос на сделку `accept_request()`
- 3N: [T] Уведомление об одобрении запроса на сделку `request_accepted_notify`
- 4: [M] Отклонить запрос на сделку `reject_request()`
- 4T: Бездействие 15мин `wait15m_on_order_request`
- 4N: [T] Уведомление об отклонении запроса на сделку `request_rejected_notify`
- 5: [B] Перевод сделки в состояние "оплачено", c отправкой чека `mark_payed(receipt)`
- 5N: [S] Уведомиление продавца об оплате `payed_notify`
- 6T: Бездействие 15мин `wait15m_on_order_creaed`
- 6: [B] Отмена сделки `cancel_order()`
- 6N: [S] Уведомиление продавцу об отмене оредера покупателем `order_canceled_notify`
- 7: [S] Подтвердить получение оплаты `confirm()`
- 7N: [B] Уведомиление покупателю об успешном завершении продавцом `order_completed_notify`
- 8T: Бездействие 10мин `wait10m_on_payed`
- 8N: [S,B] Уведомление о наступлении возможности подать аппеляцию `appeal_available_notify`
- 9,10: [S,B] Подать аппеляцию cо скриншотом/видео/файлом `start_appeal(file)`
- 9N,10N: [S,B] Уведомление о поданной на меня аппеляци `appeal_started`
- 11,12: [S,B] Встречное оспаривание полученной аппеляции cо скриншотом/видео/файлом `dispute_appeal(file)`
- 11N,12N: [S,B] Уведомление о встречном оспаривание поданной аппеляции `dispute_appeal(file)`
- 13T: [S] Бездействие продавца 3часа `seller_wait3h_on_appeal`
- 14T: [B] Бездействие покупателя 3часа `buyer_wait3h_on_appeal`
- 13N: [S,B] Уведомление о завершении сделки по аппеляции `order_completed_by_appeal`
- 14N: [B,S] Уведомление об отмене сделки по аппеляции `order_canceled_by_appeal`
- 15: [B,S] Отмена аппеляции`cancel_appeal()`
- 15N: [B,S] Уведомление об отмене аппеляции против меня `appeal_canceled`
- 16: Отправка сообщения юзеру в чат по ордеру с приложенным файлом `send_order_msg(msg:str, file=None)`
- 16N Получение сообщения в чате по ордеру `get_order_msg => (msg:str, file=None)`
- 17: Отправка сообщения по апелляции `send_appeal_msg(file, msg:str=None)`
- 17N: Получение сообщения по апелляции `get_appeal_msg => msg:str`

### Scheme
```mermaid
flowchart TD
T1((T)) -->|"`1: [T] **Creates**`"| 1[Requested]

1 .->|1N: Request Notify|M1((M))

M1 ==>|"`3: [M] **Accepts**`"| 3[Created]

subgraph Rejected
  2(["[T] Request Canceled"]):::red
  4(["[M] Rejected"]):::red
end

M1 ==x|"`4: [M] **Rejects**`"| 4
1 --x|4T: Wait 15m| 4
1 ==x|"`2: [T] **Cancels**`"| 2

2 .->|2N: Taker cancel\norder request| M2((M))
4 .->|4N: Maker reject\norder request| T2((T))

3 ==>|"`5: [B] **Marks: PAYED**<br>(with Receipt?)`"| 5[PAYED]
3 .-> |3N: Request\nAcepted Notify| T3((T))
3 ---x|6T: Delay 15m| 6(((by<br>buyer))):::red
3 ===x|"`6: [B] **Cancels**`"| 6

Payed ==>|"`7: [S] **Confirms**`"| 7(((By<br>Seller))):::green
7 .->|7N: Seller Completed order| B4((B))

S2 -->|Delay 3h| 13

subgraph Payed
subgraph Completed
direction TB
13(((By\nAppeal))):::green
7
end
    5 -->|8T: Wait 10m| 8(PAYED +10m)
    5 .-> |5N: Order\nPayed Notify| S1((S))
    15(Appeal Canceled)
    8 .->|8N: Appeal Available| B3((B))
    8 .->|8N: Appeal Available| S3((S))

    B2 <-->|17,17N| SP
    subgraph Appeal
      subgraph ABB [By Buyer]
        10 .->|10N: Buyer started appeal| S2((S))
        S2 ==>|"`12: **No! I've no payment**<br>(with Screenshot)`"|12{{"[B] Appeal\nDisputed"}}
      end
      SP((Sp))
      subgraph ABS [By Seller]
        9 .->|9N: Seller started appeal| B2((B))
        B2 ==>|"`11: **No! I've paid**<br>(with Receipt)`"|11{{"[S] Appeal\nDisputed"}}
      end
    S2 <-->|17,17N| SP
    end
end

Payed ==x|"`6: [B] **Cancels**`"| 6
6 .-> |6N: Buyer Canceled Order| S4((S))

B3 ==>|"`10: [B] **No release**<br>(with Receipt!)`"| 10{{Appeled<br>by Buyer}}
15 <===|"`15: [B] **Cancels<br>appeal**`"| ABB
S3 ==>|"`9: [S] **No payment**<br>(with Screenshot)`"| 9{{Appeled<br>by Seller}}
15 <===|"`15: [S] **Cancels<br>appeal**`"| ABS
15 .->|15N: Appeal  Canceled| B3
15 .->|15N: Appeal Canceled| S3


B2 -->|Delay 3h| 14(((by<br>appeal))):::red
Appeal o-->|50%: Wait for<br>sup decision| 13
Appeal o-->|50%: Wait for<br>sup decision| 14


13 .->|13N: Done by appeal| B4
13 .->|13N: Done by appeal| S4
14 .->|14N: Canceled by appeal| B4
14 .->|14N: Canceled by appeal| S4

subgraph Canceled
direction TB
6
14
end

classDef green stroke:#0f0
classDef red stroke:#f00
```
###### Legend
***[T] - Taker, [M] - Maker, [S] - Seller, [B] - Buyer***.<br>
*Clean digits (1, 2, ..)*: Simple outbound HTTP Requests;<br>
*N suffix (1N, 2N, ..)*: Inbound Notifications - from SSE/WS/Pyrogram client;<br>
*T suffix (4T, 8T, ..)*: Only Tests with idle waithing time.

### Ex (Public)
- 19: Список поддерживаемых валют тейкера `curs() => [Cur]`
- 20: Список платежных методов `pms() => [Pm]`
- 21: Список платежных методов по каждой валюте `cur_pms_map() => {Cur: [Pm]}`
- 22: Список торгуемых монет (с ограничениям по валютам, если есть) `coins() => [Coin]`
- 23: Список пар валюта/монет `pairs() => [Pair]`
- 24: Список объяв по (buy/sell, cur, coin, pm) `ads(coin: Coin, cur: Cur, is_sell: bool, pms:list[Pm]=None)`
- 42: Минимальные объемы валют в объявлении `cur_mins() => FlatDict`
- 43: Минимальные объемы монет в объявлении `coin_mins() => FlatDict`

### Fiat
- 25: Список реквизитов моих платежных методов `my_fiats(cur:Cur=None) => [Fiat]`
- 26: Создание `fiat_new(cur:Cur, pm:Pm, detail:str, type:PmType=None)`
- 27: Редактирование `fiat_upd(detail:str=None, type:PmType=None)`
- 28: Удаление `fiat_del(fiat_id:int)`

### Ad
- 29: Список моих ad `my_ads()`
- 30: Создание ad: `ad_new(coin: Coin, cur:Cur, is_sell: bool, pms:[Pm], price:float, is_float:bool=True, min_fiat:int=None, details:str=None, autoreply:str=None, status:AdvStatus=AdvStatus.active)`
- 31: Редактирование `ad_upd(pms:[Pm]=None, price:float=None, is_float:bool=None, min_fiat:int=None, details:str=None, autoreply:str=None, status:AdvStatus=None)`
- 32: Удаление `ad_del()`
- 33: Вкл/выкл объявления `ad_switch() => result: bool`
- 34: Вкл/выкл всех объявлений `ads_switch() => result: bool`

### User
- 35: Получить объект юзера по его ид `get_user(user_id) => user`
- 36: Отправка сообщения юзеру с приложенным файлом `send_user_msg(msg:str, file=None)`*
- 37: (Раз)Блокировать юзера `block_user(is_blocked:bool=True)`
- 38: Поставить отзыв юзеру `rate_user(positive:bool)`<br>
**Inbound:**
- 36N: Получение сообщения от юзера `get_user_msg => (msg:str, file=None)`
- 37N: Получение уведомления о (раз)блокировке юзером `got_blocked => is_blocked:bool`
- 38N: Получение уведомления о полученном отзыве `got_rated => (user_id:int, order_id:int)`

### Assets
- 41: Получить балансы моих монет: `my_assets() => list[Asset]`
- 40: Получить реквизиты для депозита монеты `deposit(amount: int) => bool` 
- 40N: Получена монета `deposited => amount`
- 41: Вывести монету `withdraw(amount: int) => bool`
- 41N: Монета выведена `withdrew => amount`