import urllib.request
import xml.etree.ElementTree as ET

rss_url = "https://anchor.fm/s/10cdf4708/podcast/rss"

with urllib.request.urlopen(rss_url) as response:
    xml_data = response.read()

root = ET.fromstring(xml_data)

# RSS items live under channel > item
for item in root.findall("./channel/item"):
    title = item.find("title")
    if title is not None:
        print(title.text)


# if using feedparser, this code simplifies the process:

# import feedparser

# rss_url = "https://anchor.fm/s/10cdf4708/podcast/rss"
# feed = feedparser.parse(rss_url)

# for entry in feed.entries:
# 	title = entry.get("title")
# 	print(title)

# sample output:
# Charles Babbage 1791 Augusta Ada Byron King, Countess of Lovelace 1815 - 1852
# Leonhard Euler 1707 - 1783
# Joseph Liouville 1809 - 1882
# Évariste Galois 1811 - 1832
# John F Nash 1928 - 2015
# Jules Henri Poincaré 1854 - 1912
# Johann Carl Friedrich Gauss 1777 - 1855
# Georg Friedrich Bernhard Riemann 1826 - 1866
# Johann Peter Gustav Lejeune Dirichlet 1805 - 1859
# Marie-Sophie Germain 1776 - 1831
# Carl Gustav Jacob Jacobi 1804 - 1851
# Siméon Denis Poisson 1781 - 1840
# Abraham de Moivre 1667 - 1754
# Jean Le Rond d'Alembert 1717 - 1783
# Pierre-Simon Laplace 1749 - 1827
# François Viète 1540 - 1603
# Joseph-Louis Lagrange 1736 - 1813
# Joseph Fourier 1768 - 1830- 1871
