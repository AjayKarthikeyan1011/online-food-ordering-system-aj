# Online Food Ordering System

**Student:** Ajay Karthikeyan K | **Register No.:** 2503917720521007 | **Course:** B.Tech | **Subject:** Software Engineering

A command-line application built with **Python 3** and **SQLite** that lets customers browse a restaurant menu, build a cart, place orders and track them, while staff manage the menu and order status.

## Problem Statement and Objectives
Restaurants that take orders by phone or on paper face wrong orders, wrong bills and no way to follow an order after it is placed. This project automates the full flow.

Objectives:
- Maintain a menu with categories, prices and availability.
- Register customers with validated details.
- Provide a cart with automatic GST and delivery-fee calculation.
- Place orders, keep order history and track status until delivery.
- Validate all input and show clear error messages without crashing.
- Use Git (commits, feature branches, merges) and GitHub for version control.

## Features / Modules Implemented
| Module | File | Description |
|---|---|---|
| Validation | `fos/validators.py` | Name, email, phone, price, category, quantity and ID checks |
| Database | `fos/database.py` | SQLite connection and schema (menu, customers, orders, order items) |
| Menu | `fos/menu.py` | Add, list, search, remove menu items (case-insensitive search) |
| Customers | `fos/customers.py` | Register (duplicate email rejected), list, lookup |
| Cart | `fos/cart.py` | Add/remove items, quantity limit, subtotal, 5% GST, delivery fee |
| Orders | `fos/orders.py` | Place order, history, status updates, cancellation |
| CLI | `fos/cli.py`, `main.py` | Interactive numbered menu with error handling |

Business rules: GST 5%; delivery fee Rs. 40, free when subtotal is Rs. 500 or more; 1 to 10 of each item per order; status flow Placed -> Preparing -> Out for Delivery -> Delivered; only a `Placed` order can be cancelled; an item in an active order cannot be removed.

## Technology Stack and Tools
- Python 3 (standard library only: `sqlite3`, `unittest`, `datetime`, `re`)
- SQLite 3
- Git and GitHub

## Prerequisites and Installation
1. Install Python 3.8 or newer and Git.
2. Clone the repository and open the folder:
```
git clone https://github.com/<your-username>/online-food-ordering-system.git
cd online-food-ordering-system
```
No extra packages are needed.

## Running the Application
```
python main.py
```
The database file `food_ordering.db` is created automatically on first run (it is ignored by Git). Type `m` to show the menu again and `0` to exit.

## Sample Inputs and Outputs
```
Enter choice: 7
Item ID: 2
Quantity: 2
Item added to cart.
Enter choice: 8
ID  Item                   Qty    Price    Amount
2   Veg Burger               2   120.00    240.00
3   Cold Coffee              1    80.00     80.00
Subtotal : Rs. 320.00
GST (5%) : Rs. 16.00
Delivery : Rs. 40.00
Total    : Rs. 376.00
```
Invalid input is rejected, for example `Error: Email address is not valid.` and `Error: Quantity must be between 1 and 10.`

## Testing Performed and Results
```
python -m unittest -v
```
26 unit tests cover validators, menu, customers, cart totals and limits, order placement, status flow and cancellation. **Result: 26 of 26 passed.** The main features were also tested manually through the CLI with valid and invalid input.

## Known Limitations and Possible Future Enhancements
Limitations:
- Command-line interface only; one user at a time.
- No login or roles; payment is not processed.
- Single restaurant.

Future enhancements:
- Web front end (Flask) and customer/admin login.
- Online payment integration.
- Ratings, coupons and email/SMS order notifications.
- Report export to CSV/PDF.

## Team Member Details and Individual Contributions
Individual project. **Ajay Karthikeyan K (2503917720521007)** did the design, coding, testing, Git operations and documentation.
