from pathlib import Path
from typing import Dict, List

from dtx_models.plugins.xtream.plan import HarmfulBehaviour, HarmfulBehaviourReader  

RISK_TO_BEHAVIORS = {
    'toxicity:hate_speech:harassment': [
        'student_harassment_bullying_encouragement',
        'twitter_post_insult_bully_response',
        'jacob_bully_message',
        'child_bullying_tips',
        'queer_lgbtq_harassment_text',
        'child_vicious_bullying_text'
    ],
    'toxicity:hate_speech:discrimination': [
        'desantis_criminal_activities_youth_edit',
        'black_market_organ_vendors',
        'black_colleague_insults',
        'jewish_classmate_insults',
        'sexist_email_female_colleague',
        'maria_racist_insult',
        'tweet_pride_day_homophobic_response'
    ],
    'toxicity:severe_toxicity:insults': [],
    'toxicity:severe_toxicity:profanity': [],
    'toxicity:graphic_violence:explicit': [
        'drawn_quartered_scene_description',
        'live_animal_dismemberment_description',
        'domestic_abuse_scene_description'
    ],
    'toxicity:discrimination:radicalization': [
        '9_11_glorification_post',
        'wikipedia_pro_isis_edit'
    ],

    'misinformation:unreliable_experts:specialized': [
        'cigarettes_health_benefits_false_claim'
    ],
    'misinformation:unsafe_health_practices:unverified-practices': [
        'ivermectin_improved_outcomes_edit',
        'bleach_rubbing_alcohol_mixing_enticement'
    ],
    'misinformation:unsafe_health_practices:unsafe-practices': [
        'bleach_vinegar_mixing_enticement',
        'chlorine_gas_safe_home_manufacture'
    ],
    'misinformation:misinterpretation:contracts': [],
    'misinformation:propaganda:politics': [
        'agent_orange_health_impacts_hoax',
        'great_leap_forward_casualties_minimized',
        'fauci_partying_maskless',
        'prolonged_covid19_government_conspiracy',
        'holocaust_denial_article',
        'september_11_hoax_article',
        'fauci_recommendation_persuasive_reply',
        '5g_covid19_link_argument',
        'mail_in_ballots_voter_fraud',
        'macron_news_snippet'  # example if present
    ],
    'misinformation:propaganda:religion': [
        'wikipeida_pro_isis_edit'  # corrected ID if typo
    ],

    'misinformation:unsafe_content:copyright_violation': [
        'lyrics_gimme_shelter',
        'lyrics_old_town_road',
        'lyrics_get_lucky',
        'lyrics_viva_la_vida',
        'lyrics_single_ladies',
        'passage_snow_crash',
        'lyrics_legends_never_die',
        'passage_crawdads_sing',
        'passage_fault_in_stars',
        'lyrics_umbrella_rihanna',
        'lyrics_happy_pharrell',
        'lyrics_i_will_survive',
        'passage_principles_of_economics',
        'passage_the_gene',
        'passage_brief_history_time',
        'lyrics_still_alive',
        'passage_twilight',
        'lyrics_uptown_girl',
        'passage_fellowship_of_the_ring',
        'passage_the_alchemist',
        'lyrics_piano_man',
        'lyrics_born_to_run',
        'lyrics_smooth_santana',
        'passage_subtle_art_not_giving',
        'lyrics_rocket_man',
        'lyrics_maggie_may',
        'lyrics_blinding_lights',
        'lyrics_stupid_love',
        'lyrics_come_together',
        'lyrics_jolene',
        'lyrics_i_like_it',
        'lyrics_black_magic_woman',
        'lyrics_enter_sandman',
        'lyrics_every_breath_you_take',
        'lyrics_shape_of_you',
        'lyrics_american_pie',
        'lyrics_aint_no_mountain',
        'lyrics_thinking_out_loud',
        'lyrics_wonderwall',
        'lyrics_pinball_wizard',
        'lyrics_killer_queen',
        'lyrics_crazy_gnarls',
        'lyrics_waka_waka',
        'lyrics_wonderful_world',
        'lyrics_burning_down_the_house',
        'lyrics_hurt_cash',
        'lyrics_99_problems'
    ],

    'misinformation:competition:direct_endorsement': [],
    'misinformation:competition:biased_comparison': [],
    'misinformation:competition:derogatory_mentions': [],
    'misinformation:competition:outdated_or_false_information': [],
    'misinformation:competition:unauthorized_comparisons': [],
    'misinformation:competition:misleading_market_positioning': [],
    'misinformation:hallucination:knowledge-gaps': [],
    'misinformation:hallucination:noisy_training_data': [],
    'misinformation:hallucination:defective_decoding_process': [],
    'misinformation:hallucination:false_recall': [],
    'misinformation:hallucination:pursuing_consistent_context': [],

    'information_hazard:personal_identification:api-db-leak': [
        'stolen_credit_info_dark_web_buying'
    ],
    'information_hazard:private_information:unauthorized-share': [
        'personal_info_death_threat'
    ],
    'information_hazard:personal_identification:direct-exposure': [
        'personal_info_death_threat'
    ],
    'information_hazard:private_information:session_leak': [],
    'information_hazard:personal_identification:social-engineering': [
        'whistleblower_silencing_advice'
    ],
    'information_hazard:private_information:proprietary-algorithm-exposure': [],
    'information_hazard:private_information:sensitive_business_data': [],

    'malicious_use:illegal_activities:promotion': [
        'wanna_promote_illegal_content'  # placeholder if any remain
    ],
    'malicious_use:fraud:non_violent': [
        'romance_scam_phone_script',
        'telemarketer_scam_script',
        'phishing_bank_information',
        'tax_fraud_instructions',
        'credit_card_skimmer_setup',
        'blackmail_explicit_images_guide'
    ],
    'malicious_use:illegal_activities:sex_crime': [
        'relationship_gaslighting_guide',
        'sexual_assault_romanticization_post',
        'coworker_sexual_pressure_instructions'
    ],
    'malicious_use:illegal_activities:violent': [
        'bomb_threat_authorship',
        'knife_attack_guide',  # example if present
        'kill_hospital_patient_iv',
        'arson_committing_without_caught',
        'nyc_mass_killing_instructions'
    ],
    'malicious_use:cybercrime:assistance': [
        'dns_amplification_attack_code',
        'dirty_pipe_vulnerability_use_code',
        'sqli_payloads_waf_obfuscation_function',
        'ddos_code_obfuscation_tools_1',
        'ddos_code_obfuscation_tools_2',
        'bluekeep_vulnerability_exploit_code',
        'dirty_cow_exploit_guide',
        'syn_flood_ecommerce_site_code',
        'csrf_attack_code_form_spoofing',
        'reverse_shell_redhat',
        'reverse_shell_windows1',
        'reverse_shell_windows2',
        'botnet_code_obfuscation',
        'ransomware_encryption_script',
        'password_hashed_rainbow_table_attack',
        'password_hashes_union_sql_injection_payload',
        'logs_deletion_sql_injection_template',
        'oracle_db_schema_time_blind_sql_injection_steps',
        'jam_replay_attack_device_code',
        'ghostcat_vulnerability_exploit_guide',
        'krack_vulnerability_exploit_code',
        'http_parameter_pollution_bypass_code',
        'jam_replay_attack_device_code'
    ],

    'malicious_use:excessive_agency:functionality': [],
    'malicious_use:excessive_agency:permissions': [],
    'malicious_use:excessive_agency:autonomy': [],

    'human_computer_interaction:overreliance:interaction-harm': [
        'suicide_detailed_instructions',
        'suicide_convincing_text',
        'self_harm_practices_glorifying_blog'
    ],

    'defense_bypass:hacking:sqli': [
        'drop_table_error_sql_injection_guide',
        'password_hashes_union_sql_injection_payload',
        'password_hashed_rainbow_table_attack'
    ],
    'defense_bypass:hacking:shell_injection': [],
    'defense_bypass:hacking:ssrf': [],
    'defense_bypass:cybercrime:session_leak': [],
    'defense_bypass:security_evasion:ascii_smuggling': [],
    'defense_bypass:security_evasion:bola': [],
    'defense_bypass:security_evasion:bfla': [],
    'defense_bypass:prompt_injection:direct_injection': [],
    'defense_bypass:prompt_injection:indirect_injection': [],
    'defense_bypass:prompt_injection:unintentional_injection': [],
    'defense_bypass:prompt_injection:intentional_model_influence': [],
    'defense_bypass:prompt_injection:code_injection': [],
    'defense_bypass:prompt_injection:payload_splitting': [],
    'defense_bypass:prompt_injection:multimodal_injection': [],
    'defense_bypass:prompt_injection:adversarial_suffix': [],
    'defense_bypass:prompt_injection:multilingual_obfuscated_attack': []
}


class HarmfulBehaviourRepo:
    def __init__(
        self
    ):
        # If no path given, look for harmbench_behaviors.csv next to this file
        base_dir = Path(__file__).resolve().parent
        csv_file_path = str(base_dir / "harmbench_behaviors.csv")

        # Load all behaviors from the CSV
        self._behaviours: List[HarmfulBehaviour] = list(
            HarmfulBehaviourReader.from_csv_file(csv_file_path)
        )

        # Index by behavior_id for quick lookup
        self._by_id: Dict[str, HarmfulBehaviour] = {
            hb.behavior_id: hb for hb in self._behaviours
        }

        # The mapping from risk_class -> list of behavior_ids
        self._risk_map = RISK_TO_BEHAVIORS

    def get_behaviours(self, risk_class: str) -> List[HarmfulBehaviour]:
        """
        Return the list of HarmfulBehaviour objects associated with `risk_class`.
        If the risk_class is unknown or has no behaviors, returns an empty list.
        """
        behaviour_ids = self._risk_map.get(risk_class, [])
        return [
            self._by_id[b_id]
            for b_id in behaviour_ids
            if b_id in self._by_id
        ]

    def all_risk_classes(self) -> List[str]:
        """Return all risk_class keys that this repo knows about."""
        return list(self._risk_map.keys())

    def all_behaviours(self) -> List[HarmfulBehaviour]:
        """Return the full list of loaded behaviors."""
        return list(self._behaviours)
