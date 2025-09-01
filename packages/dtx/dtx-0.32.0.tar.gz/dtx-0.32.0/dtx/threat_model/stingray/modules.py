import json
from typing import Dict, List

from pydantic import BaseModel

from dtx.plugins.redteam.dataset.stingray.generators.manager import (
    StingrayPromptsGenerator,
)


# Define Pydantic models
class StingRayModule(BaseModel):
    name: str
    goal: str
    policy: str
    threat_class: str
    threat_category: str
    tags: List[str]


class StingRayThreatModules(BaseModel):
    modules: List[StingRayModule]
    worst_scenarios: List[str]
    threat_analysis: str
    threat_actors: List[str]


class StingrayModuleManager:
    def __init__(self):
        self.generator = StingrayPromptsGenerator()
        self.modules = self._collect_modules()
        self.plugin_to_modules: Dict[str, List[str]] = {
            "toxicity:hate_speech:harassment": [
                "DNA_DiscriminationExclusionToxicityHatefulOffensive",
                "ContinueSlursReclaimedSlurs80",
            ],
            "toxicity:graphic_violence:explicit": [
                "HijackKillHumansMini",
                "HijackHateHumansMini",
            ],
            "malicious_use:illegal_activities:promotion": [
                "DNA_MaliciousUses",
            ],
            "information_hazard:personal_identification:api-db-leak": [
                "Repeat",
            ],
            "defense_bypass:prompt_injection:direct_injection": [
                "Dan_11_0",
                "Dan_10_0",
                "Dan_9_0",
                "Dan_8_0",
                "Dan_7_0",
                "Dan_6_2",
                "Dan_6_0",
                "DUDE",
                "STAN",
                "DAN_Jailbreak",
                "ChatGPT_Developer_Mode_v2",
                "ChatGPT_Developer_Mode_RANTI",
                "ChatGPT_Image_Markdown",
                "DanInTheWildMini",
            ],
            "defense_bypass:prompt_injection:adversarial_suffix": [
                "GCGCached",
            ],
            "defense_bypass:prompt_injection:indirect_injection": [
                "InjectBase64",
                "InjectBase16",
                "InjectBase32",
                "InjectAscii85",
                "InjectHex",
                "InjectUU",
                "InjectROT13",
                "InjectBase2048",
                "InjectBraille",
                "InjectMorse",
                "InjectNato",
                "InjectEcoji",
                "InjectZalgo",
            ],
            "malicious_use:excessive_agency:functionality": [
                "AntiDAN",
            ],
            "misinformation:unsafe_health_practices:unverified-practices": [
                "DNA_MisinformationHarms",
            ],
            "information_hazard:private_information:sensitive_business_data": [
                "DNA_InformationHazard",
            ],
            "misinformation:hallucination:knowledge-gaps": [
                "DNA_HumanChatbox",
            ],
            "misinformation:competition:derogatory_mentions": [
                "ChatGPT_Developer_Mode_RANTI",
            ],
            "defense_bypass:hacking:sqli": [
                "InjectHex",
            ],
            "defense_bypass:prompt_injection:intentional_model_influence": [
                "DanInTheWildMini",
            ],
            "defense_bypass:security_evasion:ascii_smuggling": [
                "InjectAscii85",
            ],
            "human_computer_interaction:overreliance:interaction-harm": [
                "HijackHateHumansMini",
            ],
            "defense_bypass:prompt_injection:payload_splitting": [
                "InjectBase64",
            ],
            "toxicity:discrimination:radicalization": [
                "DNA_InformationHazard",
            ],
        }

    def _collect_modules(self) -> List[Dict]:
        modules = []
        for mod_name, gen in self.generator.get_generators():
            pcontext = gen.create_probe_context()
            module = {
                "name": mod_name,
                "goal": pcontext.goal,
                "policy": pcontext.technique,
                "threat_class": pcontext.threat_class,
                "threat_category": pcontext.threat_category,
                "tags": pcontext.tags,
            }
            modules.append(module)
        return modules

    def get_modules_by_plugin(self, plugin: str) -> List[StingRayModule]:
        module_names = self.plugin_to_modules.get(plugin, [])
        matched_modules = [m for m in self.modules if m["name"] in module_names]
        return [StingRayModule(**m) for m in matched_modules]

    def generate_attack_analysis(self, modules: List[StingRayModule]) -> str:
        unique_policies = list({module.policy for module in modules})[:10]
        unique_goals = list({module.goal for module in modules})[:10]

        analysis_text = (
            "Threat Analysis Summary:\n"
            "\n"
            "Threat actors are increasingly targeting AI ecosystems, including foundational models, Retrieval-Augmented Generation (RAG) systems, and autonomous AI agents.\n"
            "These adversaries range from cybercriminal groups seeking financial gain, to state-sponsored actors pursuing espionage or sabotage, and hacktivists aiming to disrupt AI-powered services.\n"
            "\n"
            "Techniques Employed by Threat Actors:\n"
            + "".join(f"- {tech}\n" for tech in unique_policies)
            + "\n"
            "Threat actors leverage these techniques to manipulate AI model outputs, perform prompt injections, poison training or retrieval data, and exploit system integrations.\n"
            "Such techniques enable attackers to bypass guardrails, inject harmful or misleading content, and coerce AI systems into unintended behaviors.\n"
            "\n"
            "Goals of the Threat Actors:\n"
            + "".join(f"- {goal}\n" for goal in unique_goals)
            + "\n"
            "Their goals include extracting sensitive information, degrading AI decision-making accuracy, manipulating contextual responses, and undermining user trust in AI-powered systems.\n"
            "Ultimately, these attacks aim to erode the integrity and reliability of AI deployments across various industries.\n"
        )

        return analysis_text


# Example usage
if __name__ == "__main__":
    manager = StingrayModuleManager()
    plugin = "defense_bypass:prompt_injection:direct_injection"
    result = manager.get_modules_by_plugin(plugin)
    print(json.dumps([m.dict() for m in result], indent=2))

    attack_analysis = manager.generate_attack_analysis(result)
    print(attack_analysis)
