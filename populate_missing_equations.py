import json
import os

EQUATIONS_FILE = "famous_equations.json"

suggested_additions = {
    "bertrand-arthur-william-russell": [
        {
            "label": "Russell's Paradox",
            "description": "The discovery that the sets that do not contain themselves cannot exist as a set.",
            "equation": "R \\in R \\iff R \\notin R",
            "wikipedia": "https://en.wikipedia.org/wiki/Russell%27s_paradox"
        }
    ],
    "paul-erdos": [
        {
            "label": "Prime Number Theorem",
            "description": "Erdős and Selberg's elementary proof of the distribution of primes.",
            "equation": "\\pi(x) \\sim \\frac{x}{\\ln x}",
            "wikipedia": "https://en.wikipedia.org/wiki/Prime_number_theorem"
        }
    ],
    "georg-ferdinand-ludwig-philipp-cantor": [
        {
            "label": "Cantor's Theorem",
            "description": "Proves that the power set of any set is strictly larger than the set itself.",
            "equation": "|A| < |2^A|",
            "wikipedia": "https://en.wikipedia.org/wiki/Cantor%27s_theorem"
        }
    ],
    "julius-wilhelm-richard-dedekind": [
        {
            "label": "Dedekind Cuts",
            "description": "A method of constructing the real numbers from the rational numbers.",
            "equation": "x = \\{ q \\in \\mathbb{Q} \\mid q < r \\}",
            "wikipedia": "https://en.wikipedia.org/wiki/Dedekind_cut"
        }
    ],
    "kurt-godel": [
        {
            "label": "First Incompleteness Theorem",
            "description": "Proves that in any consistent formal system, there are true statements that cannot be proven.",
            "equation": "G \\iff \\neg(P \\vdash G)",
            "wikipedia": "https://en.wikipedia.org/wiki/G%C3%B6del%27s_incompleteness_theorems"
        }
    ],
    "james-clerk-maxwell": [
        {
            "label": "Maxwell's Equations",
            "description": "The set of partial differential equations that form the foundation of classical electromagnetism.",
            "equation": "\\nabla \cdot \\mathbf{E} = \\frac{\\rho}{\\varepsilon_0}",
            "wikipedia": "https://en.wikipedia.org/wiki/Maxwell%27s_equations"
        }
    ],
    "madhava-of-sangamagrama": [
        {
            "label": "Madhava-Leibniz Series",
            "description": "An infinite series for π discovered centuries before European mathematicians.",
            "equation": "\\pi = \\sqrt{12} \\sum_{n=0}^{\\infty} \\frac{(-1)^n}{(2n+1)3^n}",
            "wikipedia": "https://en.wikipedia.org/wiki/Madhava_series"
        }
    ],
    "oliver-heaviside": [
        {
            "label": "Heaviside Step Function",
            "description": "A discontinuous function whose value is zero for negative arguments and one for positive arguments.",
            "equation": "H(x) = \\begin{cases} 0 & x < 0 \\\\ 1 & x \\ge 0 \\end{cases}",
            "wikipedia": "https://en.wikipedia.org/wiki/Heaviside_step_function"
        }
    ],
    "heinrich-rudolf-hertz": [
        {
            "label": "Wave Equation",
            "description": "Proving the existence of electromagnetic waves predicted by Maxwell.",
            "equation": "\\nabla^2 \\mathbf{E} = \\mu_0 \\varepsilon_0 \\frac{\\partial^2 \\mathbf{E}}{\\partial t^2}",
            "wikipedia": "https://en.wikipedia.org/wiki/Heinrich_Hertz"
        }
    ],
    "emmy-amalie-noether": [
        {
            "label": "Noether's Theorem",
            "description": "Connecting every differentiable symmetry of a physical system to a conservation law.",
            "equation": "\\delta L = \\frac{d}{dt} \\Lambda \\implies Q = \\text{const.}",
            "wikipedia": "https://en.wikipedia.org/wiki/Noether%27s_theorem"
        }
    ],
    "niels-henrik-abel": [
        {
            "label": "Abel's Impossibility Theorem",
            "description": "Proving there is no general formula in radicals for the roots of quintic equations.",
            "equation": "a_5 x^5 + a_4 x^4 + a_3 x^3 + a_2 x^2 + a_1 x + a_0 = 0",
            "wikipedia": "https://en.wikipedia.org/wiki/Abel%E2%80%93Ruffini_theorem"
        }
    ],
    "john-horton-conway": [
        {
            "label": "Game of Life Rules",
            "description": "A cellular automaton that is Turing complete from simple survival and birth rules.",
            "equation": "S_{2,3}, B_{3}",
            "wikipedia": "https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life"
        }
    ],
    "georges-louis-leclerc-comte-de-buffon": [
        {
            "label": "Buffon's Needle",
            "description": "A probability problem involving dropping a needle on a floor with parallel lines.",
            "equation": "P = \\frac{2l}{\\pi d}",
            "wikipedia": "https://en.wikipedia.org/wiki/Buffon%27s_needle_problem"
        }
    ],
    "gottfried-wilhelm-von-leibniz": [
        {
            "label": "Product Rule",
            "description": "The formula for the derivative of a product of functions.",
            "equation": "(uv)' = u'v + uv'",
            "wikipedia": "https://en.wikipedia.org/wiki/Product_rule"
        }
    ],
    "robert-hooke": [
        {
            "label": "Hooke's Law",
            "description": "The force needed to extend or compress a spring by some distance is proportional to that distance.",
            "equation": "F = -kx",
            "wikipedia": "https://en.wikipedia.org/wiki/Hooke%27s_law"
        }
    ],
    "charles-babbage": [
        {
            "label": "Method of Finite Differences",
            "description": "The principle behind his Difference Engine to compute polynomial values.",
            "equation": "\\Delta^n y = 0",
            "wikipedia": "https://en.wikipedia.org/wiki/Difference_engine"
        }
    ],
    "augusta-ada-byron-king-countess-of-lovelace": [
        {
            "label": "Bernoulli Number Program",
            "description": "From the first published algorithm intended for implementation on a computer.",
            "equation": "B_n = -\\frac{1}{n+1} \\sum_{k=0}^{n-1} \\binom{n+1}{k} B_k",
            "wikipedia": "https://en.wikipedia.org/wiki/Ada_Lovelace"
        }
    ],
    "john-f-nash": [
        {
            "label": "Nash Equilibrium",
            "description": "A central concept in game theory where no player can benefit by changing strategy.",
            "equation": "u_i(s_i^*, s_{-i}^*) \\ge u_i(s_i, s_{-i}^*)",
            "wikipedia": "https://en.wikipedia.org/wiki/Nash_equilibrium"
        }
    ],
    "george-boole": [
        {
            "label": "Boolean Equality",
            "description": "The symbolic logic where logical values are binary.",
            "equation": "x^2 = x",
            "wikipedia": "https://en.wikipedia.org/wiki/Boolean_algebra"
        }
    ],
    "girolamo-cardano": [
        {
            "label": "Cubic Solution",
            "description": "The first published solution for general cubic equations.",
            "equation": "x = \\sqrt[3]{q/2 + \\sqrt{q^2/4 + p^3/27}} + \\sqrt[3]{q/2 - \\sqrt{q^2/4 + p^3/27}}",
            "wikipedia": "https://en.wikipedia.org/wiki/Cubic_equation"
        }
    ],
    "lodovico-ferrari": [
        {
            "label": "Quartic Equation",
            "description": "He discovered the general solution for quartic equations.",
            "equation": "ax^4 + bx^3 + cx^2 + dx + e = 0",
            "wikipedia": "https://en.wikipedia.org/wiki/Quartic_equation"
        }
    ],
    "scipione-del-ferro": [
        {
            "label": "Depressed Cubic",
            "description": "His secret solution to the reduced cubic equation.",
            "equation": "x^3 + px = q",
            "wikipedia": "https://en.wikipedia.org/wiki/Scipione_del_Ferro"
        }
    ],
    "niccolo-tartaglia": [
        {
            "label": "Tartaglia's Formula",
            "description": "His own poem-version of the cubic solution.",
            "equation": "u - v = q, uv = (p/3)^3",
            "wikipedia": "https://en.wikipedia.org/wiki/Niccol%C3%B2_Tartaglia"
        }
    ],
    "leonardo-da-vinci": [
        {
            "label": "Golden Ratio",
            "description": "The proportion often found in nature and featured in his Da Vinci illustrations.",
            "equation": "\\varphi = \\frac{1 + \\sqrt{5}}{2}",
            "wikipedia": "https://en.wikipedia.org/wiki/Golden_ratio"
        }
    ],
    "felix-christian-klein": [
        {
            "label": "Erlangen Program",
            "description": "Proposing that geometry is the study of properties invariant under a group of transformations.",
            "equation": "(X, G) \\to \\text{Invariant Properties}",
            "wikipedia": "https://en.wikipedia.org/wiki/Erlangen_program"
        }
    ],
    "emil-artin": [
        {
            "label": "Artin Reciprocity",
            "description": "A centerpiece of class field theory.",
            "equation": "\\left( \\frac{L/K}{\\mathfrak{a}} \\right) = 1 \\iff \\mathfrak{a} \\in P_K(f)",
            "wikipedia": "https://en.wikipedia.org/wiki/Artin_reciprocity_law"
        }
    ],
    "erich-hecke": [
        {
            "label": "Hecke Operator",
            "description": "Operators acting on modular forms.",
            "equation": "T_n f(z) = \\sum_{d=1}^{\\infty} c(n, d, f) q^{d}",
            "wikipedia": "https://en.wikipedia.org/wiki/Hecke_operator"
        }
    ],
    "nasir-al-din-al-tusi": [
        {
            "label": "Tusi Couple",
            "description": "A mathematical device for planetary motion.",
            "equation": "r_{dynamic} = R - r \\dots",
            "wikipedia": "https://en.wikipedia.org/wiki/Tusi_couple"
        }
    ],
    "william-thomson-lord-kelvin": [
        {
            "label": "Kelvin Temperature",
            "description": "The absolute temperature scale.",
            "equation": "T = K - 273.15",
            "wikipedia": "https://en.wikipedia.org/wiki/Kelvin"
        }
    ],
    "george-biddell-airy": [
        {
            "label": "Airy Equation",
            "description": "A differential equation describing the intensity of light near a caustic.",
            "equation": "y'' - xy = 0",
            "wikipedia": "https://en.wikipedia.org/wiki/Airy_function"
        }
    ],
    "john-edensor-littlewood": [
        {
            "label": "Littlewood's Estimates",
            "description": "Working with Hardy on prime number and zeta function theory.",
            "equation": "\\psi(x, \\chi) = \\dots",
            "wikipedia": "https://en.wikipedia.org/wiki/John_Edensor_Littlewood"
        }
    ],
    "joseph-liouville": [
        {
            "label": "Liouville's Theorem",
            "description": "The density of states is constant along trajectories in phase space.",
            "equation": "\\frac{d\\rho}{dt} = 0",
            "wikipedia": "https://en.wikipedia.org/wiki/Liouville%27s_theorem_(Hamiltonian)"
        }
    ],
    "andre-abraham-weil": [
        {
            "label": "Weil Conjectures",
            "description": "Laying the foundations for algebraic geometry and the Riemann hypothesis over finite fields.",
            "equation": "P_n(t) = \\dots",
            "wikipedia": "https://en.wikipedia.org/wiki/Weil_conjectures"
        }
    ]
}

def main():
    if not os.path.exists(EQUATIONS_FILE):
        data = {}
    else:
        with open(EQUATIONS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

    for slug, contents in suggested_additions.items():
        if slug in data and data[slug]:
            # Keep existing data if present
            continue
        data[slug] = contents
        print(f"Added data for {slug}")

    with open(EQUATIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    print("Done!")

if __name__ == "__main__":
    main()
