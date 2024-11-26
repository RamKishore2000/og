import razorpay  # Razorpay client library
import webview  # Use pywebview instead of webview
from kivymd.app import MDApp
from kivy.lang import Builder
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.boxlayout import BoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from kivymd.uix.screen import Screen
from kivy.uix.scrollview import ScrollView

# Razorpay API credentials (Test Mode)
RAZORPAY_KEY_ID = 'rzp_test_hf2afT5lk394ug'
RAZORPAY_KEY_SECRET = 'bSTTNZLyxYZXdNzb2aRUHLvT'
user_wallet = {'balance': 0}

# Initialize Razorpay client
client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

# Initialize wallet balance
wallet_balance = 0  # This will keep track of the wallet balance

def create_razorpay_order(amount_in_paise):
    try:
        order_data = client.order.create({
            "amount": amount_in_paise,
            "currency": "INR",
            "receipt": "receipt#1",
            "payment_capture": 1
        })
        if order_data.get("id"):
            print(f"Razorpay Order Created Successfully: {order_data['id']}")
            return order_data
        else:
            print("Error: Order data does not contain an ID")
            return None
    except Exception as e:
        print(f"Error creating Razorpay order: {str(e)}")
        return None

class Kishore(MDApp):
    def build(self):
        self.screen = Screen()

        # Create a ScrollView to handle the UI components in case of small screens
        scroll = ScrollView()
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)

        # Display wallet balance
        self.wallet_label = MDLabel(text=f"Wallet Balance: {user_wallet['balance']} INR", theme_text_color="Primary")
        layout.add_widget(self.wallet_label)

        # Input field for amount
        self.amount_input = MDTextField(hint_text="Enter Amount", mode="rectangle", size_hint=(1, None), height=40)
        layout.add_widget(self.amount_input)

        # Pay Now button
        pay_button = MDRaisedButton(text="Pay Now", size_hint=(1, None), height=50, on_release=self.pay_now)
        layout.add_widget(pay_button)

        # View Wallet Balance button
        

        # Add layout to ScrollView and the screen
        scroll.add_widget(layout)
        self.screen.add_widget(scroll)

        return self.screen

    def pay_now(self, instance):
        """
        Function to handle the payment process when 'Pay Now' is clicked.
        It creates an order on Razorpay and opens Razorpay checkout in a pywebview.
        """
        # Get the entered amount from the MDTextInput field
        amount_input = self.amount_input.text

        if not amount_input:
            # Show an alert dialog if no amount is entered
            dialog = MDDialog(
                title="Error",
                text="Please enter a valid amount",
                size_hint=(0.7, 1)
            )
            dialog.open()
            return

        try:
            # Convert the amount to paise (1 INR = 100 paise)
            amount_in_paise = int(amount_input) * 100
        except ValueError:
            # Show an error dialog if the amount is invalid
            dialog = MDDialog(
                title="Invalid Amount",
                text="Please enter a valid number",
                size_hint=(0.7, 1)
            )
            dialog.open()
            return

        # Create order and get order details from Razorpay API
        order_data = create_razorpay_order(amount_in_paise)
        if order_data:
            order_id = order_data['id']
            amount = order_data['amount']
            currency = order_data['currency']

            # Create Razorpay checkout options in HTML/JavaScript
            checkout_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
            <script src="https://checkout.razorpay.com/v1/checkout.js"></script>
            </head>
            <body>
                <script>
                    var options = {{
                        key: '{RAZORPAY_KEY_ID}',  // Razorpay API Key
                        amount: {amount},  // Amount in paise (integer)
                        currency: '{currency}',
                        name: 'Your Company',
                        description: 'Test Payment',
                        order_id: '{order_id}',  // Order ID from Razorpay API
                        handler: function(response) {{
                            alert('Payment successful: ' + response.razorpay_payment_id);
                            // Call payment success handler to update wallet
                            window.pywebview.api.payment_success(response.razorpay_payment_id, {amount});
                        }},
                        modal_error: function(response) {{
                            alert('Payment failed: ' + response.error.description);
                        }},
                        prefill: {{
                            name: 'John Doe',
                            email: 'john.doe@example.com',
                            contact: '8639028233',
                        }},
                        theme: {{
                            color: '#F37254'
                        }}
                    }};
                    var rzp1 = new Razorpay(options);
                    rzp1.open();
                </script>
            </body>
            </html>
            """

            # Directly open the Razorpay checkout HTML in the webview
            self.open_payment_modal(checkout_html)

    def open_payment_modal(self, html_content):
        """
        Function to open Razorpay payment modal directly from the HTML content string.
        :param html_content: The HTML content that includes the Razorpay checkout script
        """
        try:
            # Open Razorpay checkout using pywebview directly from the HTML string
            webview.create_window("Razorpay Payment", html=html_content, width=360, height=640, js_api=self)
            webview.start()
        except Exception as e:
            print(f"Error opening Razorpay payment modal: {e}")

    

    def update_wallet(self, amount_in_paise):
        """
        Function to update the wallet balance when a successful payment is made.
        :param amount_in_paise: The amount to be credited to the wallet
        """
        global wallet_balance
        wallet_balance += amount_in_paise / 100  # Convert paise to INR
        self.wallet_label.text = f"Wallet Balance: ₹{wallet_balance:.2f}"

    def payment_success(self, payment_id, amount):
        """
        Simulate payment success and update wallet balance.
        :param payment_id: Payment ID received after a successful transaction
        :param amount: Amount credited to the wallet
        """
        # Simulate the success of the payment (this part could be connected to a real payment verification)
        self.update_wallet(amount)
        self.show_dialog("Payment Successful", f"Payment of ₹{amount / 100} was successful!")

    def show_dialog(self, title, text):
        """
        Function to show a simple dialog to the user.
        """
        dialog = MDDialog(
            title=title,
            text=text,
            size_hint=(0.7, 1)
        )
        dialog.open()

if __name__ == "__main__":
    Kishore().run()


