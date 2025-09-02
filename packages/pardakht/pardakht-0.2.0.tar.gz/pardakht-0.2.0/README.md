# Pardakht 💰

**Pardakht** is a simple Python library to integrate bots or applications with payment gateways.  
Currently, it supports **ZarinPal** and **PayPing**.

![Downloads](https://static.pepy.tech/personalized-badge/pardakht?period=total&units=international_system&left_color=grey&right_color=blue)

---
## Installation

```bash
pip install pardakht
````
---
## Usage

### 1️⃣ ZarinPal Integration

#### Import and Initialize

```python
from pardakht.dargah import ZarinPal

# Settings
MERCHANT_ID = "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"
CALLBACK_URL = "https://yourdomain.com/check-payment"

# Create an instance of ZarinPal
zarinpal = ZarinPal(merchant_id=MERCHANT_ID, callback_url=CALLBACK_URL, sandbox=True)
```

#### Create a Payment and Get the Payment Link

```python
amount = 10000  # Amount in Tomans
uuid_code = "some-unique-id-1234"  # You can use uuid.uuid4() for unique transactions
description = "Premium subscription purchase"

pay_url = zarinpal.make_payment(amount, uuid_code, description)

if pay_url.startswith("http"):
    print("Payment link:", pay_url)
else:
    print("Error:", pay_url)
```

> ⚡ If there is an issue connecting to the gateway, it will return:  
> `"Failed to connect to the payment gateway."`

#### Verify the Payment After User Returns from Gateway

```python
authority = "A1B2C3D4E5"  # Obtained from query params or gateway payload
result = zarinpal.verify_payment(authority, amount)

if result["success"]:
    print("Payment successful ✅")
    print("Tracking code:", result["ref_id"])
else:
    print("Payment failed ❌")
    print("Message:", result["message"])
```

---

### 2️⃣ PayPing Integration

#### Import and Initialize

```python
from pardakht.dargah import PayPing

# Settings
API_KEY = "YOUR_PAYPING_API_KEY"

# Create an instance of PayPing
payping = PayPing(api_key=API_KEY)
```

#### Create a Payment and Get the Payment Link

```python
amount = 10000  # Amount in your currency unit
return_url = "https://yourdomain.com/callback"
payer_identity = "user@example.com"
description = "Premium subscription purchase"

payment_data = payping.create_payment(
    amount=amount,
    return_url=return_url,
    payer_identity=payer_identity,
    description=description
)

# Extract payment code to start the payment
payment_code = payment_data.get("metaData", {}).get("code")

if payment_code:
    pay_url = payping.start_payment(payment_code)
    print("Payment link:", pay_url)
else:
    print("Error creating payment:", payment_data)
```

#### Verify the Payment After User Returns from Gateway

```python
ref_id = "REF_ID_FROM_CALLBACK"  # Obtained from callback parameters
payment_code = "PAYMENT_CODE"    # The same code returned from create_payment

result = payping.verify_payment(ref_id, payment_code)

if result.get("status") == 0:
    print("Payment verified successfully ✅")
else:
    print("Payment verification failed ❌")
    print("Details:", result)
```

---
### 3️⃣ Notes
- Always generate a **unique ID (uuid)** for each ZarinPal transaction to track it in your database.
- Store **payment code and ref_id** for PayPing transactions to verify later.
- In **Telegram bots**, you can use `pay_url` as an inline button for users to click.
- Use `sandbox=True` during testing in ZarinPal to avoid real transactions.
- Handle **errors gracefully** and validate the response from each gateway before confirming the transaction.