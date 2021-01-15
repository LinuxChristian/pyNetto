#!/usr/bin/env python
from datetime import datetime
import quopri
from bs4 import BeautifulSoup
import pandas as pd
import imaplib


def convert_to_us_decimal(s):
    """
    Given a string with EU decimal formatting return a US formatted price
    E.g. 3,00 -> 3.00

    Parameters
    ----------
    s : str
        Number as string to convert

    Returns
    -------
    out : String with corrected decimal seperator
    """
    return s.replace(".", "").replace(",", ".")


def connect_to_imap(server, user, passwd):
    """Connect to IMAP server

    Parameters
    ----------
    server : str
        URL to the IMAP server (e.g. imap.google.com)
    user : str
        Username to the IMAP server
    passwd : str
        Password to the IMAP server

    Returns
    -------
    out : Connection to the server
    """
    # create an IMAP4 class with SSL
    imap = imaplib.IMAP4_SSL(server)
    if user == "" or passwd == "":
        raise RuntimeError("Please update the script with our IMAP username and/or password")

    # authenticate
    imap.login(user, passwd)

    return imap


def process_emails(imap, folder):
    """Process all emails from Netto in a specific folder

    Parameters
    ----------
    imap : imaplib connection
        Connection to your IMAP server. From the `connect_to_imap` function.
    folder : str
        Folder where you store your Netto emails (e.g. "INBOX")

    Returns
    -------
    out : Pandas Dataframe with all your purchases. The dataframe contains the following
        columns,

        - time: The time of purchase
        - product: Name of the product
        - amount: Number of product purchases
        - price: The price paid
    """
    # Get emails
    status, messages = imap.select(folder, readonly=True)
    status, messages = imap.search("utf-8", 'FROM', '"noreply@netto.dk"')

    dfs = []
    for msg in messages[0].split():
        # Get the email body (i.e. content) and when it was sent
        status, response = imap.fetch(msg, '(BODY[TEXT] INTERNALDATE)')
        msg_info, msg_body = response[0]

        # Get message datetime - E.g. 23-Jul-2020 12:02:04 -0400 -> local time
        msg_time = imaplib.Internaldate2tuple(msg_info)
        msg_time = datetime(msg_time.tm_year, msg_time.tm_mon, msg_time.tm_mday,
                            msg_time.tm_hour, msg_time.tm_min, msg_time.tm_sec)

        # Convert the email body encoded in quoted-printable to text
        utf8_msg = quopri.decodestring(msg_body)

        soup = BeautifulSoup(utf8_msg, features="lxml")

        # Find the first HTML table in the message body
        table = soup.find("table")

        try:
            rows = list()
            # Iterate all HTML rows in the table and process every row of class `items`
            for row in table.findAll("tr"):
                if "items" in row.attrs["class"]:
                    # The row (tr) has three data elemets (td)
                    # Produce name - amount - price
                    product, amount, price = row.findAll("td")
                    clean_price = price.text.strip()

                    # Handle bottle pant
                    if "pant" in clean_price:
                        # A product with pant is listed as: 4.50\n+ pant 3.00
                        clean_price, pant_item = clean_price.split('\n+')
                        pant_price = convert_to_us_decimal(pant_item.split('pant')[1].strip())

                        # Add pant as seperate item
                        rows.append({
                            "time": msg_time,
                            "product": "Pant",
                            "amount": 1,
                            "price": float(pant_price)
                        })

                    # Remove newline charaters and make amount a number
                    rows.append({
                        "time": msg_time,
                        "product": product.text.strip(),
                        "amount": int(amount.text.replace("stk", "").strip()),
                        "price": float(convert_to_us_decimal(clean_price))
                    })
        except Exception as e:
            raise RuntimeError(f"Error: unable to process item {row} from {msg_time}") from e

        df = pd.DataFrame(rows)
        dfs.append(df)

    # Logout of email
    imap.logout()

    if len(dfs) == 0:
        raise RuntimeError(f"Error: could not find any emails from Netto in {EMAIL_FOLDER}")

    # Combine into a single dataframe
    ddf = pd.concat(dfs)
    return ddf


if __name__ == "__main__":
    #
    # UPDATE HERE WITH YOUR OWN SETTINGS
    #
    # Remember to update the values below to match your email provider
    IMAP_SERVER = "imap.fastmail.com"
    USERNAME = ''
    PASSWORD = ''
    EMAIL_FOLDER = "Netto"  # Email folder where you store your NETTO emails - E.g. INBOX

    conn = connect_to_imap(IMAP_SERVER, USERNAME, PASSWORD)
    df = process_emails(conn, EMAIL_FOLDER)

    # The dataframe (df) contains the following columns,
    # - time: The time of purchase
    # - product: Name of the product
    # - amount: Number of product purchases
    # - price: The price paid

    print("------ Welcome to pyNetto ------")
    print(f"Processed {df.time.nunique()} emails from Netto\n")

    # Products grouped by type - sum amount and price
    unique_products = df.groupby('product').sum()
    average_per_trip = df.groupby('time').price.sum().agg(["mean", "std"])

    print("You have in total (DKK) spent,")
    print(unique_products.price.sum())

    print(f"\n\nOn average you spend {average_per_trip['mean']:.2f} DKK per shopping trip")

    print("\n\nYour most purchased product is,")
    print(unique_products.sort_values(by='amount', ascending=False).head(1))

    print("\n\nYour most expensive product is,")
    print(unique_products.sort_values(by='price', ascending=False).head(1))
