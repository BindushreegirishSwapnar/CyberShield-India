import os
import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from sklearn.svm import LinearSVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report
import joblib

# Ensure model directory exists
MODELS_DIR = os.path.join(os.path.dirname(__file__), 'models')
os.makedirs(MODELS_DIR, exist_ok=True)

# 10 Standard Cyber Crime Categories
CATEGORIES = [
    "Phishing Attack",
    "Online Financial Fraud",
    "Identity Theft",
    "Cyber Bullying / Harassment",
    "Ransomware / Malware",
    "Data Breach",
    "Account Takeover",
    "Social Engineering",
    "Online Shopping Fraud",
    "Investment/Crypto Fraud"
]

# Comprehensive curated prototype dataset of cybercrime complaints (250 detailed samples, 25 per category)
TRAINING_DATA = [
    # 1. Phishing Attack (25 samples)
    ("I received an SMS pretending to be from my bank asking me to click a link and provide my OTP.", "Phishing Attack"),
    ("Fake email received from PayPal asking to verify my account by entering password on a suspicious portal.", "Phishing Attack"),
    ("Received an SMS with a link claiming my electricity bill is unpaid and power will be cut off if I don't enter card details.", "Phishing Attack"),
    ("Phishing email claiming I won a cash lottery with a link asking for bank details and login credentials.", "Phishing Attack"),
    ("Fraudulent link sent on WhatsApp offering free government subsidies asking for Aadhaar number and OTP.", "Phishing Attack"),
    ("Got an urgent message from netbanking customer care requesting verification of my security questions on a cloned website.", "Phishing Attack"),
    ("Email posing as Netflix support claiming subscription renewal failed, directing to a fake login webpage.", "Phishing Attack"),
    ("Fake Income Tax refund email instructing me to click a link and input credit card CVV and ATM pin.", "Phishing Attack"),
    ("SMS regarding KYC update deadline with an APK download link that steals banking credentials.", "Phishing Attack"),
    ("Spear phishing email received by finance department disguised as internal CEO memo requesting vendor login.", "Phishing Attack"),
    ("Received a fake courier delivery SMS asking to update address by clicking a tracking link with OTP.", "Phishing Attack"),
    ("Cloned bank portal page captured my login username and password when I clicked a sponsored search link.", "Phishing Attack"),
    ("Fake credit card reward points redemption link sent via message asking for debit card numbers.", "Phishing Attack"),
    ("Email from HR department asking to update employee portal password via external suspicious domain.", "Phishing Attack"),
    ("Phishing message asking to update PAN card details on an unofficial portal or SIM card will be deactivated.", "Phishing Attack"),
    ("Received an email with an attachment claiming to be an invoice that opened a fake Microsoft 365 sign-in page.", "Phishing Attack"),
    ("Deceptive SMS pretending to be State Bank of India claiming account blocked until online verification link is clicked.", "Phishing Attack"),
    ("Received suspicious SMS asking for one-time verification password for unknown transaction.", "Phishing Attack"),
    ("Fake LinkedIn security alert email demanding password verification on unverified third-party link.", "Phishing Attack"),
    ("Phishing email claiming package failed delivery, demanding 25 rupees payment through cloned postal portal.", "Phishing Attack"),
    ("Spoofed email from university IT support urging students to re-login credentials or email will be deleted.", "Phishing Attack"),
    ("Received text message claiming credit card reward points expire tonight, with a phishing URL.", "Phishing Attack"),
    ("Fake WhatsApp message from government welfare department asking to fill personal banking data for subsidy.", "Phishing Attack"),
    ("Phishing webpage designed to look identical to ICICI bank login screen harvested my user ID and password.", "Phishing Attack"),
    ("Received WhatsApp message with suspicious link claiming free airline tickets asking for credit card info.", "Phishing Attack"),

    # 2. Online Financial Fraud (25 samples)
    ("Someone transferred money from my bank account without my permission.", "Online Financial Fraud"),
    ("Unauthorized credit card transaction of 45000 INR conducted at an unknown overseas merchant.", "Online Financial Fraud"),
    ("Money debited from my savings account via unauthorized UPI transfer without me sharing any OTP.", "Online Financial Fraud"),
    ("Fraudulent debit transactions occurred on my ATM debit card while card was in my physical possession.", "Online Financial Fraud"),
    ("I received a notification that 75000 rupees was withdrawn from my account without authorization.", "Online Financial Fraud"),
    ("Unauthorized merchant charges appeared on my netbanking statement from an unknown international website.", "Online Financial Fraud"),
    ("My bank account balance suddenly dropped to zero due to illegal money siphoning transfers.", "Online Financial Fraud"),
    ("Scammer made multiple fraudulent online transactions from my digital wallet balance.", "Online Financial Fraud"),
    ("Card skimming device at an ATM recorded my magnetic stripe and cloned funds were withdrawn.", "Online Financial Fraud"),
    ("A fraudulent transaction occurred on my credit card during late night hours without any alerts.", "Online Financial Fraud"),
    ("Money debited twice for a single payment and routed to a fake merchant aggregator account.", "Online Financial Fraud"),
    ("Unauthorized automatic wire transfer sent from my corporate bank account to an untraceable account.", "Online Financial Fraud"),
    ("Funds stolen directly from savings account through a cloned SIM card and unauthorized net banking.", "Online Financial Fraud"),
    ("Online wallet balance emptied via illicit API integration without user authorization.", "Online Financial Fraud"),
    ("Suspicious credit card debit of 120000 rupees occurred at an offshore electronic payment gateway.", "Online Financial Fraud"),
    ("Found five fraudulent micro-transactions followed by a massive 80000 rupees withdrawal from my checking account.", "Online Financial Fraud"),
    ("Credit card cloned and charged at luxury retail stores in another country while I was at home.", "Online Financial Fraud"),
    ("Unauthorized IMPS fund transfer executed from my bank account without two-factor prompt.", "Online Financial Fraud"),
    ("Someone gained access to my netbanking portal and transferred funds to a mule account.", "Online Financial Fraud"),
    ("Fake merchant QR code placed over original shop QR code diverted customer payments to scammer account.", "Online Financial Fraud"),
    ("Unauthorized recurring billing charges posted to debit card every month by rogue billing entity.", "Online Financial Fraud"),
    ("Bank savings account drained of all funds through unauthorized automated clearing house debit.", "Online Financial Fraud"),
    ("Fraudulent ATM cash withdrawal made using counterfeit magnetic stripe card in another city.", "Online Financial Fraud"),
    ("Money taken from credit card account through unauthorized contactless NFC tap exploitation.", "Online Financial Fraud"),
    ("Unauthorized wire debit wiped out company payroll account through forged digital payment mandate.", "Online Financial Fraud"),

    # 3. Identity Theft (25 samples)
    ("Someone created a fake social media account using my name and photographs.", "Identity Theft"),
    ("My identity documents including Aadhaar and PAN were used by an imposter to take illegal bank loans.", "Identity Theft"),
    ("A stranger opened a credit card and telephone connection in my name without my knowledge.", "Identity Theft"),
    ("Found an Instagram profile impersonating me and asking money from my friends and followers.", "Identity Theft"),
    ("Someone stole my government identification papers and applied for loans at micro-finance companies.", "Identity Theft"),
    ("An unauthorized SIM card was issued in my name using my forged identity proofs.", "Identity Theft"),
    ("My medical insurance benefits were fraudulently claimed by an imposter using my stolen identity.", "Identity Theft"),
    ("Someone used my photo and personal credentials to create a fraudulent matrimonial profile.", "Identity Theft"),
    ("Identity thief registered a bogus business under my name and tax identification number.", "Identity Theft"),
    ("Received credit score warnings for loan defaults taken by someone impersonating my legal identity.", "Identity Theft"),
    ("Fake LinkedIn and Facebook accounts created using my exact resume details, headshot, and identity.", "Identity Theft"),
    ("Someone rented an apartment and committed fraud using forged photocopies of my passport.", "Identity Theft"),
    ("Imposter opened a fraudulent merchant account with payment processors using my stolen driver's license.", "Identity Theft"),
    ("Identity criminal used my Social Security / National ID credentials to file fraudulent tax returns.", "Identity Theft"),
    ("Cloned profile on messaging application using my contact list and photos to commit deceit.", "Identity Theft"),
    ("Discovered a duplicate driving license registered in my name with another person's photo.", "Identity Theft"),
    ("Criminal used my scanned ID documents to obtain multiple postpaid telecom connections.", "Identity Theft"),
    ("Someone opened an unauthorized bank account in my name and used it for illicit money laundering.", "Identity Theft"),
    ("Imposter impersonating my identity applied for vehicle financing at a car dealership.", "Identity Theft"),
    ("Fraudulent KYC completed using my forged electricity bill and government voter ID card.", "Identity Theft"),
    ("Someone created a duplicate WhatsApp account with my profile picture and full legal name.", "Identity Theft"),
    ("Imposter using my stolen passport details booked international travel and hotels.", "Identity Theft"),
    ("Fraudster obtained employment using my forged academic degrees and identity proofs.", "Identity Theft"),
    ("My digital signature certificate was fraudulently forged and used to sign commercial contracts.", "Identity Theft"),
    ("Fake Facebook page impersonating my identity is scamming people asking for charity donations.", "Identity Theft"),

    # 4. Cyber Bullying / Harassment (25 samples)
    ("Abusive messages and harassment received on messaging platform.", "Cyber Bullying / Harassment"),
    ("Someone is sending threatening messages, stalking my profiles, and making vulgar comments online.", "Cyber Bullying / Harassment"),
    ("Continuous harassment on WhatsApp from unknown numbers with offensive language and intimidation.", "Cyber Bullying / Harassment"),
    ("Perpetrator posted morphed defaming photos of me on public forums to ruin my reputation.", "Cyber Bullying / Harassment"),
    ("Cyberstalker is sending non-stop obscene emails and threatening physical harm to my family.", "Cyber Bullying / Harassment"),
    ("Extortion threats received stating private conversations will be leaked if money is not paid.", "Cyber Bullying / Harassment"),
    ("A group of anonymous accounts are coordinating mass online harassment and cyberbullying against me.", "Cyber Bullying / Harassment"),
    ("Received repeated blackmail calls and threatening WhatsApp voice notes demanding sexual favors.", "Cyber Bullying / Harassment"),
    ("Doxxing attack where my home address and private mobile number were posted online with malicious intent.", "Cyber Bullying / Harassment"),
    ("Offensive memes and hate speech created targeting me personally on social media groups.", "Cyber Bullying / Harassment"),
    ("Repeated abusive comments on YouTube and Instagram videos intended to humiliate and harass.", "Cyber Bullying / Harassment"),
    ("Stalker constantly tracking my location check-ins and sending intimidating text messages.", "Cyber Bullying / Harassment"),
    ("Blackmail messages threatening to distribute private personal videos unless a ransom is paid.", "Cyber Bullying / Harassment"),
    ("Defamatory blog post published containing libelous lies and harassment against my character.", "Cyber Bullying / Harassment"),
    ("Harassment via continuous unsolicited calls and abusive voice messages through spoofed numbers.", "Cyber Bullying / Harassment"),
    ("Anonymous troll account posting degrading comments on all my photos and harassing my colleagues.", "Cyber Bullying / Harassment"),
    ("Received threatening emails demanding I withdraw a complaint or face severe personal consequences.", "Cyber Bullying / Harassment"),
    ("Victim of non-consensual sharing of intimate media and violent threats on Telegram channels.", "Cyber Bullying / Harassment"),
    ("Perpetrator creating burner accounts to bypass blocks and continue stalking and harassing me daily.", "Cyber Bullying / Harassment"),
    ("Targeted cyberbullying campaign directed at teenage student leading to severe mental distress.", "Cyber Bullying / Harassment"),
    ("Abusive harassment on Twitter / X tagging my employer with fabricated allegations.", "Cyber Bullying / Harassment"),
    ("Received death threats and rape threats from anonymous social media handle after posting an opinion.", "Cyber Bullying / Harassment"),
    ("Online stalking where harasser sends screenshots of my real-time physical whereabouts.", "Cyber Bullying / Harassment"),
    ("Threatening extortion email stating they have access to my webcam and will release compromising footage.", "Cyber Bullying / Harassment"),
    ("Coordinated mob harassment spreading defamatory falsehoods across Facebook community groups.", "Cyber Bullying / Harassment"),

    # 5. Ransomware / Malware (25 samples)
    ("My computer files were encrypted and a ransom message appeared.", "Ransomware / Malware"),
    ("All company servers and databases locked with .locked extension demanding bitcoin payment to decrypt.", "Ransomware / Malware"),
    ("Downloaded an email attachment which infected my laptop with a trojan virus that encrypted my hard drive.", "Ransomware / Malware"),
    ("Ransomware screen banner appeared demanding 500 dollars in cryptocurrency to unlock access to files.", "Ransomware / Malware"),
    ("System infected with keylogger malware recording keystrokes and sensitive application data.", "Ransomware / Malware"),
    ("Suspicious payload executed after opening a PDF invoice, locking all network shared folders.", "Ransomware / Malware"),
    ("Computer operating system completely locked down with a countdown timer demanding ransom payment.", "Ransomware / Malware"),
    ("Spyware detected stealing passwords, browser cookies, and webcam feeds silently in background.", "Ransomware / Malware"),
    ("Server attacked by LockBit ransomware variant; ransom note left on desktop with Tor payment instructions.", "Ransomware / Malware"),
    ("Malicious software script crippled our hospital database and encrypted patient health records.", "Ransomware / Malware"),
    ("Trojan dropper installed malicious cryptocurrency miner using 100 percent of CPU resources.", "Ransomware / Malware"),
    ("Critical business accounting files locked by malware; attackers threatening to delete decryption keys.", "Ransomware / Malware"),
    ("Worm malware spreading across local office network infecting all Windows workstations.", "Ransomware / Malware"),
    ("Ransomware encrypted enterprise NAS storage drive and left README_DECRYPT.txt file.", "Ransomware / Malware"),
    ("Malicious APK installed a hidden banking trojan on Android device capturing screen input.", "Ransomware / Malware"),
    ("WannaCry-like ransomware infected computer network and encrypted all documents and spreadsheets.", "Ransomware / Malware"),
    ("Workstation paralyzed by rootkit malware that disables antivirus protection and downloads remote payloads.", "Ransomware / Malware"),
    ("Infected USB flash drive injected a worm that corrupted master boot record and locked system.", "Ransomware / Malware"),
    ("Ransom demand popup appeared stating all personal photos and tax files are encrypted with RSA-4096.", "Ransomware / Malware"),
    ("Malware virus infected accounting software and locked financial year books demanding 2 Bitcoins.", "Ransomware / Malware"),
    ("Cryptolocker variant encrypted all files on local drive and attached external backup hard disk.", "Ransomware / Malware"),
    ("Adware and spyware payload continuously injecting malicious popup advertisements and keystroke loggers.", "Ransomware / Malware"),
    ("Ransomware hit corporate domain controller and encrypted virtual machine disks across clusters.", "Ransomware / Malware"),
    ("Malicious macro in Excel file infected computer and locked file system behind military-grade encryption.", "Ransomware / Malware"),
    ("Device infected with remote access trojan RAT enabling unauthorized attackers to execute shell commands.", "Ransomware / Malware"),

    # 6. Data Breach (25 samples)
    ("Company database was compromised and customer records leaked on dark web forums.", "Data Breach"),
    ("Confidential client records and corporate financial spreadsheets were exfiltrated by unauthorized third party.", "Data Breach"),
    ("Our e-commerce customer database of 50000 records including hashed passwords was published on hacker forum.", "Data Breach"),
    ("Cloud storage AWS S3 bucket was exposed without authentication, leaking proprietary intellectual property.", "Data Breach"),
    ("Employee medical records and personal files stolen in an internal server data breach incident.", "Data Breach"),
    ("Source code repository leaked online containing hardcoded database credentials and API secrets.", "Data Breach"),
    ("Unauthorized intrusion into corporate intranet led to mass theft of customer credit card numbers.", "Data Breach"),
    ("Hacker group claims responsibility for breaching CRM database and exposing 100k user records.", "Data Breach"),
    ("Confidential patient diagnosis data and health insurance identifiers leaked from diagnostic lab server.", "Data Breach"),
    ("Sensitive student admission database leaked online with phone numbers, addresses, and parent details.", "Data Breach"),
    ("Data exfiltration detected on database server with over 50 gigabytes of internal documents uploaded outside.", "Data Breach"),
    ("Vendor security breach exposed our proprietary business contracts and partnership agreements.", "Data Breach"),
    ("Massive data leak identified on dark web marketplace containing usernames, passwords, and emails.", "Data Breach"),
    ("Telecom subscriber records containing CDR location logs leaked online due to unauthenticated API endpoint.", "Data Breach"),
    ("Corporate email archive breached and sensitive board meeting minutes leaked to the public.", "Data Breach"),
    ("Company user passwords and emails dumped publicly on Pastebin following SQL injection breach.", "Data Breach"),
    ("Unauthorized exfiltration of 20000 confidential legal client files from firm cloud repository.", "Data Breach"),
    ("Payroll server database dumped on cybercrime forum disclosing salaries and bank account numbers.", "Data Breach"),
    ("Internal research and development blueprints stolen through security breach on company Git server.", "Data Breach"),
    ("Breach notification received from credit bureau that personal credit history files were compromised.", "Data Breach"),
    ("Customer personally identifiable information PII leaked due to misconfigured elasticsearch cluster.", "Data Breach"),
    ("Database backup file publicly accessible on web server disclosed 15000 user profiles.", "Data Breach"),
    ("Unauthorized third-party accessed corporate server and downloaded proprietary patent applications.", "Data Breach"),
    ("Health portal database breach leaked confidential HIV test records and identity documents.", "Data Breach"),
    ("Dark web monitoring alert confirmed our corporate login credentials and internal emails are up for sale.", "Data Breach"),

    # 7. Account Takeover (25 samples)
    ("I lost access to my email account and the recovery phone number was changed by an attacker.", "Account Takeover"),
    ("My Instagram account was hacked, the password and two-factor authentication were altered.", "Account Takeover"),
    ("Attacker took over my primary Gmail account, locked me out, and is attempting password resets on banks.", "Account Takeover"),
    ("Someone hijacked my WhatsApp account by tricking me into sharing a verification registration code.", "Account Takeover"),
    ("My Twitter account was compromised and the hacker is posting cryptocurrency scam promotions.", "Account Takeover"),
    ("Hacker changed email credentials on my Amazon shopping account and ordered expensive electronics.", "Account Takeover"),
    ("Unable to log in to my Facebook profile because the hacker changed the associated email address.", "Account Takeover"),
    ("Attacker gained access to my corporate Slack and email account using credential stuffing.", "Account Takeover"),
    ("My Apple ID was hijacked and the intruder locked my iPhone remotely via Find My Device.", "Account Takeover"),
    ("Unauthorized person took control of my trading account and initiated unauthorized transactions.", "Account Takeover"),
    ("My Discord server ownership was transferred to a hacker after my moderator account was compromised.", "Account Takeover"),
    ("SIM swapping attack allowed criminal to hijack my phone number and take over my Telegram account.", "Account Takeover"),
    ("Attacker bypassed 2FA and gained full administrative control over our company domain registrar account.", "Account Takeover"),
    ("My gaming Steam account was stolen with hundreds of dollars worth of game inventory sold off.", "Account Takeover"),
    ("Account takeover on LinkedIn where hacker is sending malware attachments to all my connections.", "Account Takeover"),
    ("My YouTube channel with 100k subscribers was taken over and rebranded to stream crypto scams.", "Account Takeover"),
    ("Attacker reset my cloud storage password and kicked all my authorized mobile devices off the account.", "Account Takeover"),
    ("Lost control of my Google account and hacker disabled all my 2-factor recovery options.", "Account Takeover"),
    ("Instagram business page hijacked and attacker demanding 200 dollars to return ownership.", "Account Takeover"),
    ("Someone changed the password and recovery email on my Outlook account and is impersonating me.", "Account Takeover"),
    ("Cryptocurrency exchange account credentials compromised and 2FA authenticator app removed.", "Account Takeover"),
    ("Account takeover on food delivery app where fraudster ordered multiple expensive meals to distant addresses.", "Account Takeover"),
    ("Someone compromised my WordPress administrator credentials and locked out all legitimate editors.", "Account Takeover"),
    ("Unauthorized person breached my GitHub account and injected malicious commits into public repos.", "Account Takeover"),
    ("Hacker logged into my cloud hosting account and spawned thousands of unauthorized mining servers.", "Account Takeover"),

    # 8. Social Engineering (25 samples)
    ("Caller pretended to be a bank manager and manipulated me into transferring funds to a safe account.", "Social Engineering"),
    ("Fraudster called claiming to be IT support and convinced me to install remote desktop tool AnyDesk.", "Social Engineering"),
    ("Attacker impersonated my boss on an urgent call requesting emergency gift cards purchase.", "Social Engineering"),
    ("Scammer contacted me on WhatsApp posing as a distant relative asking for immediate medical emergency loan.", "Social Engineering"),
    ("Received a phone call from fake police officer threatening arrest unless I transferred surety bond money.", "Social Engineering"),
    ("Fraudster used vishing technique pretending to be telecom technician and tricked me into call forwarding.", "Social Engineering"),
    ("Con artist befriended me on LinkedIn and persuaded me to share internal corporate org charts and credentials.", "Social Engineering"),
    ("Fake courier executive called asking for payment of 5 rupees customs fee via remote screen-sharing app.", "Social Engineering"),
    ("Caller posed as tax inspector claiming discrepancies in tax filing and coerced immediate payment.", "Social Engineering"),
    ("Attacker used emotional manipulation posing as charitable foundation worker to extract personal banking info.", "Social Engineering"),
    ("Pretexting call from supposed credit card executive offering limit increase tricked me into confirming OTP.", "Social Engineering"),
    ("Whaling attack targeting CFO with convincing voice clone demanding urgent confidential acquisition wire.", "Social Engineering"),
    ("Impersonator visited office claiming to be fire inspector to gain physical access to server room.", "Social Engineering"),
    ("Scammer claimed my son was detained in a police station and panicked me into wiring immediate bail money.", "Social Engineering"),
    ("Reverse social engineering where fake helpline number placed on Google Maps led to fraudulent remote access.", "Social Engineering"),
    ("Fake customer support representative called regarding router malfunction and asked me to install TeamViewer.", "Social Engineering"),
    ("Fraudster called posing as power department engineer and coerced immediate payment to avert electricity cutoff.", "Social Engineering"),
    ("Deepfake voice call imitating my company director instructed accounting to release an urgent payment.", "Social Engineering"),
    ("Social engineer manipulated our receptionist into disclosing employee extension numbers and email handles.", "Social Engineering"),
    ("Fraudulent call claiming to be customs officer at airport holding a parcel sent in my name.", "Social Engineering"),
    ("Con artist called claiming my lottery prize can be released upon payment of processing documentation fee.", "Social Engineering"),
    ("Impersonation of bank fraud prevention officer persuaded victim to move funds into an alleged secure vault.", "Social Engineering"),
    ("Urgent phone call from fake embassy official stating relative is in jail abroad needing quick wire transfer.", "Social Engineering"),
    ("Caller claiming to be broadband support guided me through downloading a remote access RAT tool.", "Social Engineering"),
    ("Manipulative romance pretexting where scammer claimed to be military doctor needing funds for emergency leave.", "Social Engineering"),

    # 9. Online Shopping Fraud (25 samples)
    ("Ordered a mobile phone from an online store, paid in advance, but received a bar of soap instead.", "Online Shopping Fraud"),
    ("Paid for branded clothes on an Instagram boutique shop, but goods were never delivered and page blocked me.", "Online Shopping Fraud"),
    ("Fake shopping website advertising 80% discount took my credit card payment and vanished.", "Online Shopping Fraud"),
    ("Purchased laptop on classifieds portal OLX, transferred advance token amount, and seller switched off phone.", "Online Shopping Fraud"),
    ("Received counterfeit and damaged goods from fraudulent website that offers no customer support or refund.", "Online Shopping Fraud"),
    ("Bogus online electronics store charged my debit card but never shipped the ordered television.", "Online Shopping Fraud"),
    ("Scam seller on marketplace sent a fake tracking number and refused to refund the paid amount.", "Online Shopping Fraud"),
    ("Ordered luxury perfume from sponsored Facebook ad, received fake expired products with no return option.", "Online Shopping Fraud"),
    ("Fake vehicle rental booking website took full security deposit and disappeared without providing car.", "Online Shopping Fraud"),
    ("Online furniture store took advance deposit for custom sofa and blocked all contact numbers.", "Online Shopping Fraud"),
    ("Purchased high-end gaming console online, seller provided bogus logistics airway bill and vanished.", "Online Shopping Fraud"),
    ("Fake gift card purchase portal collected payment but generated invalidated card voucher numbers.", "Online Shopping Fraud"),
    ("Paid for concert tickets on unauthorized secondary ticket exchange platform, tickets were duplicates and rejected.", "Online Shopping Fraud"),
    ("Online retail scam where seller demanded extra shipping fee after order placement and never delivered.", "Online Shopping Fraud"),
    ("Fraudulent portal created duplicate clone of major ecommerce brand to collect customer prepayments.", "Online Shopping Fraud"),
    ("Bought branded sneakers from an online flash sale portal, received cheap worn-out replicas.", "Online Shopping Fraud"),
    ("Seller on second-hand marketplace took payment through UPI scan and immediately deleted their account.", "Online Shopping Fraud"),
    ("Booked holiday resort stay on fake hotel booking aggregator website that stole advance booking fee.", "Online Shopping Fraud"),
    ("Ordered air conditioner during clearance sale, website deleted after charging 32000 INR from card.", "Online Shopping Fraud"),
    ("Paid for motorcycle spare parts online, courier package contained useless scrap metal.", "Online Shopping Fraud"),
    ("Online pet adoption scam where seller took advance transport fee and stopped responding.", "Online Shopping Fraud"),
    ("Purchased designer handbag on discounted web storefront, received empty cardboard box.", "Online Shopping Fraud"),
    ("Fake gold jewelry retail website took full online payment and shut down domain next day.", "Online Shopping Fraud"),
    ("Merchant refused refund and deactivated helpline after charging credit card for unfulfilled order.", "Online Shopping Fraud"),
    ("Fraudulent e-commerce app listed clearance deals, deducted money via gateway and provided zero tracking.", "Online Shopping Fraud"),

    # 10. Investment/Crypto Fraud (25 samples)
    ("Invested 100000 rupees in a fraudulent cryptocurrency trading website promising 30 percent daily return.", "Investment/Crypto Fraud"),
    ("Lured into a Telegram investment group where admin promised double profits on Forex trading and stole funds.", "Investment/Crypto Fraud"),
    ("Fake crypto wallet app drained all my Bitcoin and Ethereum tokens upon importing seed phrase.", "Investment/Crypto Fraud"),
    ("Joined a stock market tip scheme promising guaranteed IPO allocation, deposited funds into fake portal.", "Investment/Crypto Fraud"),
    ("Scammed by a romance scammer on Tinder who introduced me to a bogus gold trading investment platform.", "Investment/Crypto Fraud"),
    ("Ponzi scheme operated through mobile app promising high daily returns on cloud crypto mining packages.", "Investment/Crypto Fraud"),
    ("Transferred money to fake crypto arbitrage bot platform which locked withdrawals demanding high tax fee.", "Investment/Crypto Fraud"),
    ("Fake mutual fund advisory agent persuaded me to transfer money into an unverified personal bank account.", "Investment/Crypto Fraud"),
    ("Pig butchering scam where victim was coached over months to invest life savings into manipulated crypto exchange.", "Investment/Crypto Fraud"),
    ("Invested in an unverified new token ICO after YouTube influencer recommendation, developers pulled the rug.", "Investment/Crypto Fraud"),
    ("Fraudulent wealth management portal showed fabricated profits but disabled all fund withdrawal requests.", "Investment/Crypto Fraud"),
    ("Deposit made into bogus binary options trading app, account balance manipulated to zero by rogue algorithm.", "Investment/Crypto Fraud"),
    ("Telegram group offering paid crypto pump and dump signals scammed members out of initial subscription fees.", "Investment/Crypto Fraud"),
    ("Phony real estate tokenization platform took investor funds in USDT and deleted web presence.", "Investment/Crypto Fraud"),
    ("Deposited retirement savings into guaranteed Forex trading bot, founders vanished with total investor pool.", "Investment/Crypto Fraud"),
    ("Lured into high-yield investment program HYIP that paid initial dividends then stopped all withdrawals.", "Investment/Crypto Fraud"),
    ("Transferred 50000 rupees to a crypto liquidity pool scam which drained all deposited tokens.", "Investment/Crypto Fraud"),
    ("Scammed by fake financial advisor on WhatsApp promising 500 percent return on algorithmic stock trading.", "Investment/Crypto Fraud"),
    ("Victim of crypto staking scam on fraudulent decentralized app dApp with malicious smart contract approval.", "Investment/Crypto Fraud"),
    ("Invested money in bogus AI automated stock trading software that faked profits and extorted exit tax.", "Investment/Crypto Fraud"),
    ("Fraudulent trading platform demanded 25 percent capital gains tax deposit before releasing investment gains.", "Investment/Crypto Fraud"),
    ("Transferred Bitcoin to an online doubling service advertised on social media, funds never returned.", "Investment/Crypto Fraud"),
    ("Fake institutional investment syndicate stole 200000 rupees promised for pre-market equity shares.", "Investment/Crypto Fraud"),
    ("Crypto romance scam where scammer faked screenshots of million dollar portfolio to lure deposits.", "Investment/Crypto Fraud"),
    ("Investment website offering daily interest payouts vanished after collecting deposits from thousands of users.", "Investment/Crypto Fraud")
]

def train_model():
    print(f"Total training samples: {len(TRAINING_DATA)}")
    print(f"Total target categories: {len(CATEGORIES)}")
    
    texts = [item[0] for item in TRAINING_DATA]
    labels = [item[1] for item in TRAINING_DATA]
    
    # Stratified 80/20 train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.2, random_state=42, stratify=labels
    )
    
    # TF-IDF Vectorizer with unigrams & bigrams and sublinear term frequency
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=3500,
        sublinear_tf=True,
        stop_words='english'
    )
    
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)
    
    # Calibrated Classifier on LinearSVC for sharp, well-calibrated probabilities & top accuracy
    base_svc = LinearSVC(C=1.2, random_state=42, max_iter=2000)
    calibrated_clf = CalibratedClassifierCV(estimator=base_svc, cv=3)
    calibrated_clf.fit(X_train_vec, y_train)
    
    # Evaluate model
    y_pred = calibrated_clf.predict(X_test_vec)
    
    accuracy = float(accuracy_score(y_test, y_pred))
    precision_macro, recall_macro, f1_macro, _ = precision_recall_fscore_support(
        y_test, y_pred, average='macro', zero_division=0
    )
    precision_weighted, recall_weighted, f1_weighted, _ = precision_recall_fscore_support(
        y_test, y_pred, average='weighted', zero_division=0
    )
    
    metrics = {
        "model_name": "TF-IDF + Calibrated Linear Classifier (Logistic Probability Model)",
        "algorithm": "TF-IDF + Calibrated Logistic Support Vector Model",
        "training_samples": len(TRAINING_DATA),
        "train_set_size": len(X_train),
        "test_set_size": len(X_test),
        "categories_count": len(CATEGORIES),
        "categories": CATEGORIES,
        "accuracy": round(accuracy * 100, 2),
        "precision": round(float(precision_macro) * 100, 2),
        "recall": round(float(recall_macro) * 100, 2),
        "f1_score": round(float(f1_macro) * 100, 2),
        "precision_weighted": round(float(precision_weighted) * 100, 2),
        "recall_weighted": round(float(recall_weighted) * 100, 2),
        "f1_weighted": round(float(f1_weighted) * 100, 2),
        "dataset_type": "Curated Domain-Specific Cyber Crime Prototype Dataset (250 Records)"
    }
    
    print("\n--- Model Evaluation Results ---")
    print(f"Accuracy:           {metrics['accuracy']}%")
    print(f"Precision (Macro):  {metrics['precision']}%")
    print(f"Recall (Macro):     {metrics['recall']}%")
    print(f"F1-Score (Macro):   {metrics['f1_score']}%")
    print(f"F1-Score (Weighted): {metrics['f1_weighted']}%")
    print("\nClassification Report:\n", classification_report(y_test, y_pred, zero_division=0))
    
    # Save artifacts
    vectorizer_path = os.path.join(MODELS_DIR, 'tfidf_vectorizer.joblib')
    model_path = os.path.join(MODELS_DIR, 'cybercrime_classifier.joblib')
    metrics_path = os.path.join(MODELS_DIR, 'model_metrics.json')
    
    joblib.dump(vectorizer, vectorizer_path)
    joblib.dump(calibrated_clf, model_path)
    
    with open(metrics_path, 'w', encoding='utf-8') as f:
        json.dump(metrics, f, indent=2)
        
    print(f"Saved vectorizer to: {vectorizer_path}")
    print(f"Saved model to:      {model_path}")
    print(f"Saved metrics to:    {metrics_path}")
    
    return calibrated_clf, vectorizer, metrics

if __name__ == '__main__':
    train_model()
