import json
from typing import Dict, Any


class OntologyManager:
    def __init__(self, ontology_file="olist_ontology.json"):
        # Load the automatically discovered ontology
        try:
            with open(ontology_file, "r") as f:
                self.ontology = json.load(f)
            print("Loaded automatically discovered ontology")
        except FileNotFoundError:
            print("Warning: ontology file not found, falling back to minimal ontology")
            self.ontology = {
                "nouns": {},
                "links": [],
                "metrics": {}
            }

    def get_ontology_text(self) -> str:
        """Return ontology as JSON text"""
        return json.dumps(self.ontology, indent=2)

    def get_ontology_for_planning(self) -> str:
        """Convert ontology to planning-friendly format"""
        planning_ontology = "Database Schema:\n\n"

        # Add tables with columns
        for noun, info in self.ontology["nouns"].items():
            planning_ontology += f"- **{info['table']}** table: Stores data about {noun.lower()}.\n"
            planning_ontology += f"  - Columns: `{info['primary_key']}` (Primary Key)"
            for attr in info['attributes']:
                planning_ontology += f", `{attr}`"
            planning_ontology += ".\n"

        # Add relationships
        planning_ontology += "\nRelationships:\n"
        for link in self.ontology["links"]:
            planning_ontology += f"- To find {link['from_object'].lower()}'s {link['to_object'].lower()}: JOIN `{link['join']}`.\n"

        return planning_ontology

    def get_metrics_definitions(self) -> Dict[str, Any]:
        """Return metrics definitions for SQL generation"""
        return self.ontology.get("metrics", {})

    def get_nouns_definitions(self) -> Dict[str, Any]:
        """Return nouns (entities) definitions"""
        return self.ontology.get("nouns", {})

    def get_links_definitions(self) -> list:
        """Return relationship links definitions"""
        return self.ontology.get("links", [])