# pyNetto
**pyNetto** is a small script that reads your Netto reciptes directly from your email and turns them into a Pandas Dataframe for further processing. The script contains some small examples of how to use the code.

**NOTE**: This software is not associated with Netto in any way. It is provided under a GPLv3 license without any support. Please relate any issues with the App to [Netto](https://netto.dk/kundeservice/).

## Example output

``` shell
> python pyNetto.py

------ Welcome to pyNetto ------
Processed 22 emails from Netto

You have in total (DKK) spent,
6444.75

On average you spend 292.94 per shopping trip

Your most purchased product is,
product              amount  price
LA CAM HUMMUS SPICY      17  277.0


Your most expensive product is,
product             amount  price
GÅRDKYL.FILET 280G       8  280.0
```

![alt text](https://github.com/linuxchristian/pyNetto/blob/master/Plotting_example.png?raw=true)

## Getting started
* Get the Netto Scan&Go app - [Android](https://play.google.com/store/apps/details?id=dk.dsg.scanandgo&hl=da_DK&gl=DK)/[iPhone](https://apps.apple.com/dk/app/netto-scan-go/id1424997991)
* Setup the app to send reciptes to your email and go shopping
* Install the Python dependencies required to run the script: `pip install -r requirements.txt`
* If you are running the script directly update the constants on line 155-158 to match your setting
* If you are importing the script in a notebook or seperate file read the

## Important variables
These settings are dependent upon your email provider. You can likely find the settings for your provider on their website.

- `USERNAME` : Your IMAP username (might be your email address)
- `PASSWORD` : The password to your IMAP/email account
- `IMAP_SERVER` : Your email server (e.g. `imap.google.com` or `imap.fastmail.com`)
- `EMAIL_FOLDER` : This should point to the folder where your emails are stored on the server. If all emails are in your inbox put `INBOX`.
