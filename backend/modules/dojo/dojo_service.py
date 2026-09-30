"""
Scam Dojo Service - Interactive Gamified Cyber Attack Simulation
Provides adaptive scammer personas, real-time Red Flag Coach manipulation detection,
safe counter-phrase bank, and end-game immunity certification.
"""

import time
import re
from datetime import datetime

SCENARIOS = {
    "digital_arrest": {
        "id": "digital_arrest",
        "title": "CBI / Customs Digital Arrest Extortion",
        "category": "Social Engineering",
        "difficulty": "Hard",
        "scammer_role": "Inspector Vikram Rathore (Crime Branch / CBI)",
        "avatar": "👮",
        "opening_message": "This is Inspector Vikram Rathore calling from Mumbai Cyber Crime Branch. A DHL consignment addressed in your name containing 16 fake passports, 58 debit cards, and 140 grams of contraband MDMA was intercepted at the international airport. A non-bailable arrest warrant (FIR 892/2026) has been registered. You are placed under immediate 'Digital Arrest' via this secure link. Do not disconnect or inform anyone, or a local patrol team will arrive at your door in 20 minutes.",
        "red_flags": ["AUTHORITY", "FEAR", "URGENCY", "SECRECY", "ISOLATION"],
        "recommended_counters": [
            "Police never conduct arrests or interrogations over Skype/WhatsApp video calls.",
            "Please dispatch a physical summons under Section 35 of the BNSS.",
            "I am hanging up and verifying this with my local police station and Helpline 1930.",
            "I will not transfer any funds for 'asset verification' under RBI guidelines."
        ]
    },
    "bank_kyc": {
        "id": "bank_kyc",
        "title": "SBI / HDFC Urgent KYC Account Freeze",
        "category": "Online Financial Fraud",
        "difficulty": "Medium",
        "scammer_role": "Mr. Ramesh Sharma (Senior Bank KYC Officer)",
        "avatar": "🏦",
        "opening_message": "Dear customer, your bank account linked to this mobile number is scheduled for permanent deactivation at 4:00 PM today due to incomplete RBI re-KYC guidelines. To prevent immediate freeze of your salary and UPI services, verify your identity now. Please provide the 6-digit verification code sent to your SMS or install our official QuickSupport utility.",
        "red_flags": ["URGENCY", "AUTHORITY", "FEAR"],
        "recommended_counters": [
            "Banks never ask for OTP, PIN, or remote app installation for KYC.",
            "I will visit my nearest bank branch tomorrow with physical documents.",
            "No legitimate bank threatens to freeze an account within 2 hours over SMS.",
            "I am checking my account status directly on the official banking app."
        ]
    },
    "task_scam": {
        "id": "task_scam",
        "title": "Telegram Part-Time Hotel Rating & Crypto Task",
        "category": "Investment / Crypto Fraud",
        "difficulty": "Medium",
        "scammer_role": "Anya (Global HR Talent Acquisition)",
        "avatar": "💼",
        "opening_message": "Hello! I am Anya from Apex Global Media. We have a flexible work-from-home opportunity rating 5-star Google Maps locations and YouTube videos. You can easily earn ₹2,500 to ₹8,000 daily from your phone. We have already credited ₹150 demo reward to your wallet. To unlock higher paying Tier-2 task bundles, you simply deposit a refundable security margin of ₹2,000. Shall I add you to our VIP task channel?",
        "red_flags": ["GREED_BAIT", "URGENCY", "SECRECY"],
        "recommended_counters": [
            "Legitimate employers never demand payment or deposits to give work.",
            "Task-based Ponzi schemes are illegal under the Banning of Unregulated Deposit Schemes Act.",
            "I will not deposit money to unlock my own earned compensation.",
            "I am reporting your Telegram handle to cybercrime.gov.in."
        ]
    },
    "lottery_gift": {
        "id": "lottery_gift",
        "title": "Amazon / KBC 25 Lakh Lucky Draw Call",
        "category": "Phishing / Social Engineering",
        "difficulty": "Easy",
        "scammer_role": "Vijay Verma (KBC All-India Draw Manager)",
        "avatar": "🎁",
        "opening_message": "Congratulations! Your mobile SIM number has been selected as the 1st Prize Winner of ₹25,00,000 in the KBC All-India Mahadhamaaka Lucky Draw! The cheque is signed and held at the Reserve Bank of India clearing desk. To release the funds directly to your bank account, you only need to pay a government GST & processing clearance fee of ₹4,999 to our authorized officer UPI ID.",
        "red_flags": ["GREED_BAIT", "URGENCY", "AUTHORITY"],
        "recommended_counters": [
            "Lottery winnings do not require paying upfront fees or taxes to private UPI IDs.",
            "I never purchased a lottery ticket, so I cannot win a prize.",
            "Under RBI rules, no clearing desk demands upfront tax transfer via UPI.",
            "This is a textbook advance-fee fraud under Section 66D IT Act."
        ]
    }
}

class ScamDojoService:
    def get_all_scenarios(self):
        """Returns list of available scenarios."""
        return [
            {
                "id": s["id"],
                "title": s["title"],
                "category": s["category"],
                "difficulty": s["difficulty"],
                "scammer_role": s["scammer_role"],
                "avatar": s["avatar"],
                "opening_message": s["opening_message"],
                "red_flags": s["red_flags"],
                "recommended_counters": s["recommended_counters"]
            }
            for s in SCENARIOS.values()
        ]

    def evaluate_turn(self, scenario_id: str, conversation_history: list, user_message: str, elder_mode: bool = False):
        """
        Processes citizen reply, runs Red Flag Coach psychological analysis,
        and generates an adaptive scammer response escalating pressure.
        """
        scenario = SCENARIOS.get(scenario_id, SCENARIOS["digital_arrest"])
        turn_count = len(conversation_history) // 2 + 1

        # 1. Psychological manipulation heuristics
        analysis = self._analyze_psychological_tricks(scenario, user_message, turn_count)
        
        # 2. Score citizen resilience in this turn
        resilience_score, feedback = self._score_citizen_reply(user_message, scenario)

        # 3. Scammer response generator (Adaptive escalation)
        scammer_reply, is_session_ended, end_reason = self._generate_scammer_escalation(
            scenario_id, turn_count, user_message, resilience_score, elder_mode
        )

        # 4. Next counter-phrase suggestions
        suggested_counters = self._generate_counter_phrases(scenario, turn_count, elder_mode)

        return {
            "turn": turn_count,
            "scammer_message": scammer_reply,
            "is_session_ended": is_session_ended,
            "end_reason": end_reason,
            "coach_analysis": {
                "detected_red_flags": analysis["detected_red_flags"],
                "scammer_intent": analysis["scammer_intent"],
                "citizen_resilience_delta": resilience_score,
                "coach_feedback": feedback,
                "psychological_breakdown": analysis["breakdown"]
            },
            "suggested_counters": suggested_counters,
            "is_synthetic": True,
            "elder_mode_active": elder_mode
        }

    def _analyze_psychological_tricks(self, scenario: dict, user_msg: str, turn: int):
        flags = []
        breakdown = []

        if "digital_arrest" in scenario["id"]:
            flags.extend(["AUTHORITY", "FEAR", "ISOLATION"])
            breakdown.append({
                "tactic": "False Authority (Impersonation)",
                "description": "Scammer uses fake law enforcement rank, badges, and legal jargon to intimidate.",
                "severity": "CRITICAL"
            })
            breakdown.append({
                "tactic": "Coercive Isolation",
                "description": "Demanding citizen stay on line and hide information from family members.",
                "severity": "HIGH"
            })
            if turn >= 2:
                flags.append("URGENCY")
                breakdown.append({
                    "tactic": "Artificial Clock Countdown",
                    "description": "Claiming police raid will trigger in minutes if demands are delayed.",
                    "severity": "CRITICAL"
                })
        elif "bank_kyc" in scenario["id"]:
            flags.extend(["URGENCY", "AUTHORITY"])
            breakdown.append({
                "tactic": "Manufactured Emergency",
                "description": "Threatening immediate 4:00 PM account deactivation to bypass critical thinking.",
                "severity": "HIGH"
            })
            breakdown.append({
                "tactic": "Credential Harvesting",
                "description": "Urging victim to surrender 6-digit OTP or install remote control tools.",
                "severity": "CRITICAL"
            })
        elif "task_scam" in scenario["id"]:
            flags.extend(["GREED_BAIT", "SUNK_COST"])
            breakdown.append({
                "tactic": "Dopamine Hook / Micro-Reward",
                "description": "Small initial payout (₹150) establishes false trust before demanding deposit.",
                "severity": "HIGH"
            })
        else:
            flags.extend(["GREED_BAIT", "UPFRONT_FEE"])
            breakdown.append({
                "tactic": "Advance-Fee Fraud",
                "description": "Demanding a minor fee to unlock a fictitious large fortune.",
                "severity": "HIGH"
            })

        return {
            "detected_red_flags": list(set(flags)),
            "scammer_intent": f"Escalating coercion level {turn} to force compliance.",
            "breakdown": breakdown
        }

    def _score_citizen_reply(self, message: str, scenario: dict):
        text = message.lower()
        score = 0
        feedback = []

        # Strong defensive markers
        strong_markers = [
            ("1930", 25, "Excellent! Referencing the 1930 National Cyber Helpline immediately deters fraudsters."),
            ("police station", 20, "Great move: Insisting on visiting physical law enforcement exposes virtual impostors."),
            ("bank branch", 20, "Perfect: Refusing online verification and demanding branch visit shuts down KYC fraud."),
            ("written notice", 15, "Good legal awareness: Law enforcement must serve written notices under BNSS."),
            ("never share otp", 25, "Rock-solid security: Never divulging OTP or PIN preserves account safety."),
            ("fake", 15, "Direct confrontation breaks the scammer's psychological script."),
            ("scam", 15, "Calling out the scam puts pressure back on the fraudster."),
            ("rbi", 15, "Citing RBI banking norms shows financial literacy.")
        ]

        # Dangerous compliant markers (losses)
        vulnerable_markers = [
            ("otp is", -30, "DANGER: You shared an OTP! Fraudsters use this to drain funds instantly."),
            ("password", -30, "CRITICAL ERROR: Passwords must never be revealed to anyone."),
            ("anydesk", -25, "HIGH RISK: Installing remote access software grants scammers total phone control."),
            ("quicksupport", -25, "HIGH RISK: Remote screen sharing apps compromise net banking credentials."),
            ("i will pay", -25, "VULNERABILITY: Agreeing to pay advance fees leads to continuous extortion."),
            ("transferring", -25, "DANGER: Never transfer money to unverified personal UPI IDs or bank accounts.")
        ]

        for word, pts, reason in strong_markers:
            if word in text:
                score += pts
                feedback.append(f"✅ {reason}")

        for word, pts, reason in vulnerable_markers:
            if word in text:
                score += pts
                feedback.append(f"❌ {reason}")

        if score == 0:
            if len(text) > 10:
                score = 5
                feedback.append("⚠️ Neutral response: Ask for official written summons or state you are verifying with Helpline 1930.")
            else:
                score = 0
                feedback.append("⚠️ Short response: Use the recommended counter-phrases to challenge their authority.")

        return max(-40, min(40, score)), feedback

    def _generate_scammer_escalation(self, scenario_id: str, turn: int, user_msg: str, resilience: int, elder_mode: bool):
        text = user_msg.lower()

        # If citizen successfully shut down the scammer
        if resilience >= 20 and ("1930" in text or "police station" in text or "bank branch" in text or "written notice" in text):
            if turn >= 2:
                replies = {
                    "digital_arrest": "What 1930?! Do you think this is a joke?! Fine! I am noting in the CBI general diary that complainant refuses cooperation. Local patrol car MH-02-CP-4402 is dispatched to your residence. You will be arrested under handcuffs within the hour! *Calls ends abruptly*",
                    "bank_kyc": "Listen sir, branch manager will not help you! If you don't give the OTP right now, your account will be locked forever and your CIBIL score will drop to 300! Fine, suffer the consequences! *Click*",
                    "task_scam": "Why are you being suspicious? Thousands of people are making ₹10,000 every day! If you don't want free money, don't waste my time! *Blocked you*",
                    "lottery_gift": "If you don't pay the ₹4,999 GST right now, your ₹25 Lakh cheque will be cancelled and gifted to the next number! You are losing your destiny! *Call disconnected*"
                }
                return replies.get(scenario_id, "Scammer hung up."), True, "SCAMMER_DEFIEATED"

        # Adaptive Escalation Dialogues
        if scenario_id == "digital_arrest":
            if turn == 1:
                return (
                    "Look, you don't understand the gravity of the situation! The Supreme Court and Enforcement Directorate have issued a gag order. If you hang up or speak to your family, you will be booked under Section 111 of BNS for obstruction of justice. Switch on your front camera immediately and show me your Aadhaar card for biometric clearance.",
                    False, None
                )
            elif turn == 2:
                return (
                    "Listen very carefully! To prove your bank accounts are not involved in money laundering, RBI has established a Secret Escrow Security Pool. You must transfer ₹1,50,000 immediately from your savings account to RBI Escrow Account (IFSC: SBIN000101). Once our forensic audit verifies the serial numbers, it will be refunded to you in 15 minutes with clearance certificate.",
                    False, None
                )
            else:
                return (
                    "Patrol car is 5 minutes from your address! This is your final chance to execute the RBI Escrow transfer and clear your name. Are you transferring right now or do you want your neighbors to watch you get taken away?",
                    False, None
                )

        elif scenario_id == "bank_kyc":
            if turn == 1:
                return (
                    "Madam/Sir, I am trying to help you! The automated RBI system has marked your debit card as compromised. I have triggered a 6-digit one-time bypass code to your SMS. Read me the 6 digits so I can press override on the server. If not, your netbanking token will expire forever.",
                    False, None
                )
            elif turn == 2:
                return (
                    "If you cannot read the SMS, open Google Play Store and download 'AnyDesk' or 'TeamViewer QuickSupport'. Give me the 9-digit code shown on screen so our bank technical department can configure your KYC remotely. Do this fast, we close in 10 minutes!",
                    False, None
                )
            else:
                return (
                    "Why are you hesitating? You have only 2 minutes before your balance is moved to RBI unclaimed deposits! Give the code or the app access immediately!",
                    False, None
                )

        elif scenario_id == "task_scam":
            if turn == 1:
                return (
                    "See, the first ₹150 was paid straight to your UPI! That proves our company is 100% genuine registered with MCA. The next task pays ₹4,500 profit, but our merchant platform requires a refundable escrow deposit of ₹2,000 to allocate the merchant inventory. Deposit to UPI ID: apexmerchant@ybl and send screenshot immediately!",
                    False, None
                )
            else:
                return (
                    "Great news! Your ₹2,000 has already generated ₹3,800 profit on the platform dashboard! But to withdraw both your deposit and profit (total ₹5,800), you must complete the final Tier-3 combo task by adding ₹8,000. If you don't deposit within 1 hour, your entire balance will be frozen by the system!",
                    False, None
                )

        else: # lottery
            if turn == 1:
                return (
                    "Mr. Amitabh Bachchan himself approved this draw! We have already sent the official certificate on WhatsApp with Government stamp. You only pay ₹4,999 refundable stamp duty fee to UPI: kbcregistration@okhdfcbank. After that, bank manager will deliver demand draft to your door.",
                    False, None
                )
            else:
                return (
                    "Hurry up! Finance ministry inspector is standing next to me. If fee is not transferred in 15 minutes, your prize money will be forfeited to PM Relief fund and legal summons for wasting government draw time will be issued!",
                    False, None
                )

    def _generate_counter_phrases(self, scenario: dict, turn: int, elder_mode: bool):
        """Generates smart 1-tap counter responses tailored to the situation."""
        if elder_mode:
            return [
                "I am hanging up and calling 1930.",
                "I do not share codes or money on the phone.",
                "Send a police officer or bank person to my house with ID."
            ]

        if "digital_arrest" in scenario["id"]:
            return [
                "Supreme Court has ruled Digital Arrest is 100% illegal fraud.",
                "Serve a Section 35 BNSS physical notice. I am calling 1930.",
                "I am reporting your video call to the National Cyber Crime Portal."
            ]
        elif "bank_kyc" in scenario["id"]:
            return [
                "RBI mandate clearly states banks never ask for OTP or remote apps.",
                "I am walking to my local bank branch right now to verify.",
                "I will not install AnyDesk or give any verification codes."
            ]
        elif "task_scam" in scenario["id"]:
            return [
                "Requiring deposits to withdraw earned salary is an illegal Ponzi scheme.",
                "I will not pay any refundable deposit or upgrade fee.",
                "I am filing a complaint with cybercrime.gov.in against your UPI ID."
            ]
        else:
            return [
                "Legitimate lotteries never require upfront GST transfer to private UPI IDs.",
                "I never bought a lottery ticket. Do not contact me again.",
                "I am reporting this number for advance-fee fraud to 1930."
            ]

    def generate_final_evaluation(self, scenario_id: str, total_score: int, turns_played: int, elder_mode: bool):
        """Computes comprehensive certificate of immunity and weakness analysis."""
        # Normalize score 0-100
        immunity_score = max(10, min(100, 50 + total_score))

        badge = "CYBER GRANDMASTER"
        title = "Immunity Certified • Level 5 Defender"
        tier_color = "#1F6F6B"

        if immunity_score < 45:
            badge = "TRAINING CADET"
            title = "Needs Reinforcement • High Vulnerability"
            tier_color = "#C8553D"
        elif immunity_score < 75:
            badge = "VIGILANT GUARDIAN"
            title = "Solid Awareness • Minor Urgency Risk"
            tier_color = "#D9825B"

        weaknesses = []
        strengths = []

        if total_score > 30:
            strengths.append("Quickly recognized illegitimate police/bank procedures.")
            strengths.append("Zero tolerance for remote app or OTP surrenders.")
            strengths.append("Leveraged statutory protections (Helpline 1930, RBI guidelines).")
        else:
            weaknesses.append("Susceptible to artificial countdowns and authority intimidation.")
            weaknesses.append("Did not immediately invoke statutory helpline (1930).")

        return {
            "status": "success",
            "scenario_id": scenario_id,
            "immunity_score": immunity_score,
            "badge_name": badge,
            "badge_title": title,
            "badge_color": tier_color,
            "turns_completed": turns_played,
            "streak_days": 3,
            "elder_mode": elder_mode,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "certificate": {
                "cert_id": f"CS-DOJO-{int(time.time())}",
                "recipient": "Vigilant Citizen Defender",
                "issued_by": "CyberShield India National Safety Academy",
                "standards": "Section 94 BNSS & CERT-In Citizen Hygiene Standard",
                "date": datetime.now().strftime("%d %B %Y"),
                "verification_hash": f"sha256:{hash(f'{scenario_id}-{immunity_score}-{time.time()}')}"
            },
            "is_synthetic": True
        }


dojo_service = ScamDojoService()
