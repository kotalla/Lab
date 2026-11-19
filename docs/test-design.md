# Тест-дизайн (ЛР2)

Вариант: 1


## Классы эквивалентности

| Параметр | Допустимые классы | Недопустимые классы | Представитель |
| :--- | :--- | :--- | :--- |
| **Количество (qty)** | [1; 10] | 0, -1, 11 | 1, 10 |
| **Число позиций** | [1; 5] | 0, 6 | 1, 5 |
| **Промокод** | "READMORE", "" | "WRONG", "   " | "READMORE", "" |
| **Карта лояльности** | "none", "silver", "gold" | "platinum", "" | "silver" |
| **Способ доставки** | "pickup", "courier" | "drone", "" | "courier" |
| **Имя покупателя** | [a-zA-Zа-яА-Я\s]{2,50} | "A", "" | "Иван Иванов" |
| **Почта покупателя** | regex email | "no-at-symbol", "" | "test@mail.ru" |

## Граничные значения

| Граница | Значение -1 | Значение (Граница) | Значение +1 |
| :--- | :--- | :--- | :--- |
| **MAX_ITEMS** | 4 | **5** | 6 |
| **MAX_QTY** | 9 | **10** | 11 |
| **BULK_QTY** | 9 | **10** | 11 |
| **PROMO_MIN** | 1499.99 | **1500.00** | 1500.01 |
| **FREE_DELIVERY_FROM** | 2999.99 | **3000.00** | 3000.01 |
| **MAX_DISCOUNT** | 24% | **25%** | 26% |

## Таблица решений

| Правило | Loyalty | Bulk | Promo | Результат |
|---|---|---|---|---|
| R1 | none | false | false | 0% |
| R2 | silver | false | false | 4% |
| R3 | gold | false | false | 9% |
| R4 | none | true | false | 8% |
| R5 | silver | true | false | 12% |
| R6 | gold | true | true | ограничение 27% |

## Диаграмма состояний

```mermaid

stateDiagram-v2
    [*] --> NEW
    NEW --> PAID: pay
    PAID --> SHIPPED: ship
    SHIPPED --> DELIVERED: deliver
    DELIVERED --> RETURNED: return
    NEW --> CANCELLED: cancel
    PAID --> CANCELLED: cancel
    CANCELLED --> [*]
    RETURNED --> [*]