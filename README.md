# Parseri4000

* Aja skripti: `python3 -m parser4k CONFIG`
	* Vaatii lukuoikeudet config-filun kohdekansioon. Voit joko
		a) lisätä käyttäjän sopivaan ryhmään, jolla on lukuoikeudet,
		b) lisätä lukuoikeudet "muille käyttäjille" kohdekansioon `chomod o+r`, tai
		c) ajaa roottina
* Jos on mieletön määrä headereita, käytä get\_headers -skriptiä: `python3 get_headers POLKU -d DELIMITER` config-filun luomisen apuna

