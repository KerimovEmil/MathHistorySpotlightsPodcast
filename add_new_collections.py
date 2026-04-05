import json
import os

COLLECTIONS_FILE = "collections.json"

new_collections = [
    {
        "id": "kings-of-math",
        "title": "The Kings of Mathematics",
        "tag": "The Unrivaled Titans",
        "description": "A collection dedicated to the absolute titans who dominated mathematics in the 18th and 19th centuries, fundamentally shifting every discipline they touched—from number theory to physics and topology.",
        "mathematicians": [
            {
                "slug": "leonhard-euler",
                "name": "Leonhard Euler",
                "role": "The Master of Us All",
                "image": "/assets/images/episodes/Leonhard Euler.avif"
            },
            {
                "slug": "johann-carl-friedrich-gauss",
                "name": "Johann Carl Friedrich Gauss",
                "role": "The Prince of Mathematics",
                "image": "/assets/images/episodes/Johann Carl Friedrich Gauss.avif"
            },
            {
                "slug": "georg-friedrich-bernhard-riemann",
                "name": "Bernhard Riemann",
                "role": "Geometry & Primes",
                "image": "/assets/images/episodes/Georg Friedrich Bernhard Riemann.avif"
            }
        ]
    },
    {
        "id": "foundations-of-truth",
        "title": "Foundations of Truth",
        "tag": "Logic and Infinity",
        "description": "How paradoxes and infinities broke mathematics, and the logicians who tried to fix it. These three thinkers challenged the very definition of a mathematical proof and showed us the limits of computation and truth.",
        "mathematicians": [
            {
                "slug": "georg-ferdinand-ludwig-philipp-cantor",
                "name": "Georg Cantor",
                "role": "The Master of Infinite",
                "image": "/assets/images/episodes/Georg Ferdinand Ludwig Philipp Cantor.avif"
            },
            {
                "slug": "bertrand-arthur-william-russell",
                "name": "Bertrand Russell",
                "role": "The Paradox Maker",
                "image": "/assets/images/episodes/Bertrand Arthur William Russell.avif"
            },
            {
                "slug": "kurt-godel",
                "name": "Kurt Gödel",
                "role": "Incompleteness Theorem",
                "image": "/assets/images/episodes/Kurt G\u00f6del.avif"
            }
        ]
    },
    {
        "id": "russian-probability",
        "title": "The Russian Probability School",
        "tag": "Rigorous Chance",
        "description": "While the French established early probability through gambling, it was the Russian mathematicians who turned it into a rigorous, axiomatic discipline capable of modeling complex, real-world phenomena.",
        "mathematicians": [
            {
                "slug": "andrei-andreyevich-markov",
                "name": "Andrei Markov",
                "role": "Chain Reactions",
                "image": "/assets/images/episodes/Andrei Andreyevich Markov.avif"
            },
            {
                "slug": "andrey-nikolaevich-kolmogorov",
                "name": "Andrey Kolmogorov",
                "role": "Axioms of Chance",
                "image": "/assets/images/episodes/Andrey Nikolaevich Kolmogorov.avif"
            }
        ]
    },
    {
        "id": "heavenly-mechanics",
        "title": "Mechanics of the Heavens",
        "tag": "Celestial Predictability",
        "description": "Exploring how mathematics became the ultimate language of celestial mechanics and the cosmos. These minds developed the theoretical tools needed to prove that the solar system functioned like a massive, deterministic clockwork.",
        "mathematicians": [
            {
                "slug": "joseph-louis-lagrange",
                "name": "Joseph-Louis Lagrange",
                "role": "Analytical Mechanics",
                "image": "/assets/images/episodes/Joseph-Louis Lagrange.avif"
            },
            {
                "slug": "pierre-simon-laplace",
                "name": "Pierre-Simon Laplace",
                "role": "The French Newton",
                "image": "/assets/images/episodes/Pierre-Simon Laplace.avif"
            },
            {
                "slug": "jules-henri-poincare",
                "name": "Henri Poincaré",
                "role": "The Last Universalist",
                "image": "/assets/images/episodes/Jules Henri Poincar\u00e9.avif"
            }
        ]
    }
]

def update():
    with open(COLLECTIONS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    data.extend(new_collections)
    
    with open(COLLECTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"Successfully added {len(new_collections)} new collections.")

if __name__ == "__main__":
    update()
