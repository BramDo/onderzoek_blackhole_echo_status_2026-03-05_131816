# Licentieonderzoek voor de Qiskit echo runner

**Concept voor Bram Dobbelaar | Bijgewerkt op 11 oktober 2026 | Enige auteur Bram Dobbelaar | Apache-2.0 gekozen | Nog niet gepubliceerd**

Dit document onderzoekt de herkomst van de door Elias Abebe Gasparini gevraagde code, vergelijkt softwarelicenties en bevat Engelse conceptteksten. Het verleent geen rechten. Er zijn geen bestanden, issues of reacties in GitHub gewijzigd.

**Keuze vastgelegd:** Bram Dobbelaar heeft op 11 oktober 2026 bevestigd dat hij de runner zelf heeft ontwikkeld met hulp van ChatGPT/Codex, dat uitsluitend hij als auteur wordt vermeld en dat hij Apache-2.0 kiest voor zijn eigen bijdragen. Behandel de M3-kalibratieadapter voorlopig als mogelijk aangepast IBM/M3-materiaal. Laat de externe PE-LiNN-modelcode, modelgewichten, onderzoeksgegevens, figuren, papers en overige repositorybestanden buiten deze licentie.

**Auteursvermelding:** Bram Dobbelaar is de enige auteur die voor de runner wordt vermeld, op grond van zijn eigen bevestiging. ChatGPT/Codex is een hulpmiddel en wordt niet als coauteur of rechthebbende genoemd. De afzonderlijke copyright- en bronvermeldingen voor materiaal van derden blijven behouden. **[Onbevestigd]** De exacte historische AI-sessie en eventuele bronovername zijn niet onafhankelijk volledig gereconstrueerd. De auteursverklaring verleent geen rechten van derden.

## 1 Controleerbare bevindingen

De repository is openbaar, gebruikt de branch `master` en stond bij controle op commit `78e09c48ab25b3c6ebc3fed36c483123fc057a61`. Issue 1 stond open en had nul reacties. Elias vraagt om een specifieke licentie, toepasselijke vermeldingen, herkomst en credits voor de runner en diens verklarende opmerkingen. Hij vraagt geen rechten op alle experimenten of publicaties. [1]

| Onderdeel | Vastgesteld |
| --- | --- |
| Gevraagde runner | `files/quantum-math-lab/qiskit_black_hole_hardware_runner.py` |
| Exacte Git blob | `30905b5b42a559f233527f0ea487f330cb6b1888` |
| Bestandsgrootte | 114873 bytes |
| Eerste zichtbare opname | Commit `ac38bea0f30e23d505d179c3e75747f98c7befae`, 18 maart 2026, als nieuw bestand van 1098 regels |
| Oudere runnerblob | `320201f3c9b52ce6812bdfcd255fc23048ed60fc` |
| Laatste inhoudelijke runnerwijziging | Commit `c5e6c9e7c83b5f3dbc8e204400d822cbf44bbfeb`, 22 maart 2026 |
| Bijbehorende module | `files/quantum-math-lab/qiskit_black_hole_scrambling.py` |
| Moduleblob | `a0369885f252efcb3031dd56d3167429aa903d41` |
| Licentiebestand | Geen LICENSE, COPYING of NOTICE aangetroffen in de volledige bestandsboom van deze snapshot |
| Licentieheaders | Geen SPDX-, copyright- of licentieheader aangetroffen in de 17 Pythonbestanden |

De exacte bytes van runner en module zijn ook lokaal tegen de Git-blobhash gecontroleerd. De boom bevatte 282 items en was volgens de API niet afgekapt. De onderzochte bronbestanden en geselecteerde projectnotities vermelden geen concrete externe bron voor de runner. [2, 3]

Alle 30 zichtbare commits vermelden `BramDo` of `Bram Dobbelaar` als Git-auteursnaam. De eerste runnercommit heet “docs(phase-02): archive phase2 control artifacts”. **[Afleiding] Dit is een import van eerder werk, geen sluitend verslag van de oorspronkelijke schrijfgeschiedenis.** Bram heeft vervolgens zelf bevestigd dat hij de runner ontwikkelde met hulp van ChatGPT/Codex en dat alleen hij als auteur wordt vermeld. Die verklaring is de grondslag voor de auteurscredit; de commitgeschiedenis blijft bewijs van publicatie en wijzigingen. [3]

De module begint met de verwijzing “Gebaseerd op de gedeelde ChatGPT-thread”. Er staat geen URL, datum, account of concrete mapping van gegenereerde passages bij. De beschikbare eerdere gesprekscontext leverde de oorspronkelijke thread niet op. [4]

Het paperconcept bevat een afzonderlijk auteursveld met de naam Lenna. De voorgestelde runnerlicentie omvat dat paper niet. Deze papercredit wordt niet overgenomen als auteur van de runner, waarvoor Bram Dobbelaar als enige auteur is bevestigd. Hiermee wordt geen uitspraak gedaan over de identiteit van Lenna of het auteurschap van het afzonderlijke paper. [5]

## 2 Herkomst per codeonderdeel

Regelnummers hieronder horen uitsluitend bij de geregistreerde runnerblob. Functienamen blijven bruikbaar wanneer een toekomstige licentieheader de regels verschuift.

| Onderdeel | Herkomstbeoordeling | Rechten die je kunt verlenen |
| --- | --- | --- |
| Jobafhandeling, countsconversie, logging, observabelen, statistieken en CLI van de runner | Projectspecifieke implementatie. Bram bevestigt dat hij de runner zelf ontwikkelde met AI als hulpmiddel; de precieze sessie is niet gereconstrueerd. | Apache-2.0 is gekozen voor Brams eigen beschermde bijdragen. Materiaal van derden behoudt zijn eigen voorwaarden; publicatie is nog niet uitgevoerd. |
| Lokale tensorinversie en subset/block-Z helpers | Numerieke methoden zijn herkenbaar; implementatie staat in deze repository. Geen externe tekstuele match vastgesteld buiten hergebruik binnen dezelfde repository. | Jouw eigen uitwerking indien bevestigd; de wiskundige methode zelf is geen exclusief softwareauteursrecht. |
| `_build_m3_marginal_mitigator`, regels 782–837 | Concrete overeenkomst met oudere M3-broncode, hieronder toegelicht. [Afleiding] Mogelijke adaptatie. | Geen nieuwe eigen licentie voor onderliggend IBM/M3-materiaal; eventuele eigen wijzigingen kunnen afzonderlijk worden gelicentieerd. |
| `_apply_m3_correction`, regels 840–893 | Roept de M3-API aan en verwerkt uitkomsten. Dat bewijst op zichzelf geen kopie van M3-code. | Brams eigen adapterbijdragen vallen in de gekozen Apache-2.0-scope; M3 zelf houdt zijn upstreamlicentie. |
| `_load_ml_sidecar_bundle` en `_predict_ml_sidecar_subset_echo`, regels 62–149 | Adapter laadt extern `PELiNNQEM`-model en een checkpoint. De modelimplementatie staat niet in de runner. | Brams eigen adaptercode valt in de gekozen Apache-2.0-scope. Geen rechten op het geladen model of checkpoint via deze vrijgave. |
| `brickwork_scrambler`, `build_echo_measurement_circuits`, `parse_depths` | Geïmporteerd uit de lokale scramblingmodule. Deze module verwijst naar de gedeelde ChatGPT-thread. | Afzonderlijk beoordelen. De voorgestelde scope neemt dit bestand niet automatisch mee. |
| Imports van Qiskit, Runtime, NumPy en PyTorch | Gebruik van externe bibliotheken. | Geen herlicentiëring van die bibliotheken. Hun eigen voorwaarden blijven gelden. |
| Wetenschappelijke concepten en achtergrondpapers | Echo, scrambling, Rényi-entropie en readoutinversie zijn ideeën/methoden; de bibliografie bewijst geen overgenomen code. | Geen claim op de concepten. Overgenomen tekst, figuren of code vereisen een eigen beoordeling. |

### Concreet spoor naar M3

De adapter bouwt per qubit een `float32`-matrix van 2 bij 2, kiest de bitpositie in omgekeerde volgorde, telt nulmetingen na nulvoorbereiding en éénmetingen na éénvoorbereiding, vult de twee matrixkolommen en gebruikt dezelfde vergelijking tussen de foutkans na éénvoorbereiding en de juiste nulmetingskans om defecte qubits te markeren.

Dezelfde opeenvolging staat in de marginale tak van `_job_thread` in:

`Qiskit/qiskit-addon-mthree/mthree/mitigation.py`

Vergelijkingscommit: `8402654566900aed11b64f625e18b49aefb902eb`, gedateerd 6 augustus 2025. Blob van dat bronbestand: `486105ee893f5abce0bc6006af45b8cf12506d69`. Het bestand bevat de vermelding `(C) Copyright IBM 2021.` en Apache-2.0. Dit is een versie die aantoonbaar vóór de runneruitbreiding bestond, niet een bewezen identificatie van de werkelijk gebruikte checkout. [6]

**[Afleiding] De overeenkomst is sterk genoeg om deze functie voorlopig als mogelijke M3-adaptatie te behandelen.** Het is geen bewijs dat iemand de bron letterlijk kopieerde: delen van de matrixopbouw volgen ook uit de methode. Een expliciete herkomstvermelding, behoud van de IBM-vermelding en een vermelding van wijzigingen voorkomen een ongefundeerde claim van uitsluitend oorspronkelijk werk.

De oudere runner van 18 maart bevat deze M3-adapter en de directe lokale tensorhelper nog niet. Deze zijn aanwezig in de snapshot van 22 maart. De zichtbare wijzigingsgeschiedenis lokaliseert hun opname, maar niet wie de inhoud oorspronkelijk schreef.

### PE-LiNN is een afzonderlijke rechtenbron

De runner verwijst standaard naar een extern `src/model.py`. De andere PE-LiNN-adapters in de repository noemen een lokale PELINN-Q-checkout. Eerdere context wijst naar `BramDo/PELINN-Q`.

De onderzochte PELINN-Q-licentie is MIT en vermeldt:

`Copyright (c) 2025 paolodarold`

Dit stond ook in commit `04a399f942058bf5cee761958b7d513982d848c2` van 5 januari 2026. De bijbehorende `src/model.py` bevat `PELiNNQEM` en heeft blob `d1e0c8ee68f84b49dd1c9e142d472c62924b7bf8`. **[Onbevestigd] Deze checkout is inhoudelijk passend, maar niet bewezen de exacte externe modelversie van de hardwarerun.** [7]

Je mag onder de MIT-voorwaarden toegestane handelingen met die code verrichten, maar kunt de oorspronkelijke copyrightvermelding niet vervangen door jouw naam. Repositoryeigendom en medeauteurschap van een manuscript geven geen zelfstandig bewijs dat alle modelcode van jou is. Modelgewichten en trainingsgegevens worden door deze runnerlicentie niet vrijgegeven.

## 3 Welke rechten zijn juridisch van jou

De Europese softwarerichtlijn beschermt de eigen intellectuele schepping van een auteur. Zij onderscheidt de concrete uitdrukking van software van de achterliggende ideeën en principes. Gezamenlijke menselijke auteurs kunnen gezamenlijke rechten hebben; software die in uitvoering van een dienstverband wordt geschreven kent bovendien een werkgeversregel. [8]

**[Afleiding] Je kunt dus je eigen beschermde code, eigen selectie/structuur en eigen verklarende opmerkingen licentiëren, voor zover die rechten niet zijn overgedragen en geen toestemming van andere rechthebbenden ontbreekt.** Een Git-commit met jouw naam, een geslaagde uitvoering of een eigen repository is onvoldoende om dit voor elke passage vast te stellen.

Bij AI-assistentie moet worden vastgesteld van wie de oorspronkelijke sessie was en welke dienstvoorwaarden golden. OpenAI's geraadpleegde Europese voorwaarden dragen eventuele OpenAI-rechten in output over aan de betreffende gebruiker, binnen het toepasselijke recht. Ze garanderen geen unieke output en omvatten geen rechten op output van andere gebruikers of derden. **[Afleiding] Zo'n contractuele overdracht bewijst geen auteursrecht op volledig machinaal gegenereerde passages en herstelt geen eventuele rechten van derden.** [9]

Voor AI-training is nog een afzonderlijk punt relevant: de geraadpleegde voorwaarden verbieden gebruik van output om concurrerende modellen te ontwikkelen. **[Onbevestigd] Zonder de oorspronkelijke sessie, toen geldende voorwaarden en het concrete PQID-gebruik kan ik niet bepalen of die bepaling hier van toepassing is.** Dit is geen algemene conclusie dat PQID verboden is. Een softwarelicentie maakt eventuele contractuele verplichtingen niet automatisch ongedaan. [9]

De huidige status is daarom: **Bram Dobbelaar als enige auteur bevestigd, Apache-2.0 voor zijn eigen bijdragen gekozen, bronvermeldingen voor derden behouden, publicatie nog niet uitgevoerd.**

## 4 Vergelijking van softwarelicenties

| Licentie | Hergebruik in codecollecties en AI-werk | Belangrijkste voorwaarden | Afweging |
| --- | --- | --- | --- |
| Apache-2.0 | Breed hergebruik, wijzigingen en verspreiding; geen beperking tot onderzoek | Licentiekopie, behoud relevante vermeldingen, wijzigingsvermelding; toepasselijke NOTICE-inhoud behouden. Expliciete beperkte patentlicentie met beëindigingsregel bij bepaalde patentprocedures. | [Afleiding] Beste aansluiting op het mogelijke M3-materiaal en een controleerbare herkomstregistratie. |
| MIT | Breed hergebruik met weinig administratieve voorwaarden | Copyright- en toestemmingsvermelding behouden in kopieën of substantiële delen; geen afzonderlijk uitgewerkte patentclausule | Eenvoudig voor jouw eigen bijdragen. Eventueel M3-materiaal blijft daarnaast Apache-2.0. |
| BSD-3-Clause | Vergelijkbaar breed hergebruik | Bron- en binaire verspreiding behouden toepasselijke notices; naam van rechthebbenden of bijdragers niet zonder toestemming voor endorsement gebruiken | Bruikbaar als expliciete bescherming tegen gesuggereerde aanbeveling door jou zwaar weegt. |
| GPL-3.0-only | Gebruik en verspreiding mogelijk, met copyleft bij toepasselijke afgeleide software | Broncode- en licentieverplichtingen; een verzameling van zelfstandige werken maakt niet automatisch alle andere werken GPL | Minder eenvoudig voor dit doel. Geen verbod op AI-training en geen bewezen automatische GPL-plicht voor modelgewichten. |

Bronnen: de officiële teksten van Apache, MIT en BSD en de SPDX-weergave van GPLv3. [10–13]

**Gekozen licentie: Apache-2.0, alleen voor Brams eigen bijdragen.** Dit verplicht jou tot een patentverlening voor zover de standaardclausule op jouw licentieerbare bijdragen van toepassing is. Bram heeft deze inhoudelijke keuze op 11 oktober 2026 bevestigd. Een reeds verleende Apache-licentie is volgens haar voorwaarden in beginsel onherroepelijk; een latere andere licentiekeuze haalt bestaande toestemmingen niet terug. [10]

MIT of BSD-3-Clause zijn redelijke alternatieven als je hun eenvoud of endorsementclausule verkiest. Als de M3-adaptatie wordt behouden, mogen haar Apache-voorwaarden niet verdwijnen doordat jouw bijdragen MIT of BSD krijgen. Een gecombineerde bestandsvermelding moet dan de toepasselijke licenties per onderdeel weergeven; een enkele MIT-header voor het hele bestand zou misleidend zijn.

Deze permissieve licenties zijn openbaar en algemeen. Ze geven dus ook commerciële partijen rechten binnen hun voorwaarden, niet alleen Elias of PQID. Een beperking zoals “alleen niet-commercieel onderzoek” toevoegen verandert de licentie en is geen standaard Apache-2.0 of MIT.

Creative Commons raadt zijn gebruikelijke licenties af voor software. De PQID-repository toont CC-BY-4.0, maar die datasetvermelding kan de toepasselijke softwarelicentie van ingebedde upstreamcode niet vervangen. PQID moet de bronvoorwaarden afzonderlijk behouden. [14, 15]

**[Afleiding] De ruime gebruiksrechten van Apache, MIT en BSD zijn geschikt voor de kopieer-, aanpassings- en verspreidingshandelingen rond een trainingsdataset, mits toepasselijke notices meegaan.** Dat bewijst geen toelating door PQID en beslist niet automatisch of een bepaald model of modeloutput een auteursrechtelijke bewerking is. Voor die laatste vraag ontbreken concrete gegevens.

## 5 Welke afzonderlijke vermeldingen nodig zijn

| Materiaal | Gecontroleerde upstreamlicentie | Wat afzonderlijk moet worden behouden |
| --- | --- | --- |
| Qiskit SDK | Apache-2.0 | Bij overgenomen of meegeleverde code de daadwerkelijke copyright-, licentie- en relevante attributionvermeldingen. De gecontroleerde root noemt IBM en bijdragers vanaf 2017. |
| qiskit-ibm-runtime | Apache-2.0 | Eigen upstreamnotices; gecontroleerde root noemt IBM en bijdragers vanaf 2021. |
| qiskit-aer | Apache-2.0 | Eigen upstreamnotices; gecontroleerde root noemt IBM en bijdragers vanaf 2018. Aer wordt in de scramblingmodule gebruikt. |
| M3 / mthree | Apache-2.0 | Mogelijk aangepaste kalibratiepassage: filecopyright IBM 2021, exacte bronreferentie en wijzigingsvermelding. Voor meegeleverde M3-code de volledige toepasselijke notices. |
| NumPy | BSD-3-Clause | Volledige toepasselijke copyrightvermelding, voorwaarden en disclaimer van de daadwerkelijk meegeleverde versie. |
| PyTorch | BSD-style upstreamlicentie met meerdere copyrightvermeldingen | Het volledige relevante upstreamlicentiebestand en de notices van daadwerkelijk meegeleverde onderdelen; niet terugbrengen tot alleen jouw naam. |
| PELINN-Q-modelcode | MIT | `Copyright (c) 2025 paolodarold` en de volledige MIT-tekst als dit model of substantiële delen worden gekopieerd of meegeleverd. |
| Papers, tutorialtekst, afbeeldingen en voorbeelden | Niet per object vastgesteld | Exacte bron, auteurs, versie en toepasselijke toestemming/licentie vaststellen wanneer overname blijkt. Niet automatisch door een Qiskit-package-licentie gedekt. |

De upstreamlicenties zijn inhoudelijk gelezen, niet alleen uit GitHub's licentiebadge afgeleid. De exacte historische versies van de geïnstalleerde Qiskit-, Runtime-, Aer-, M3-, NumPy- en PyTorch-packages zijn niet vastgesteld. Er is geen requirements- of lockbestand in de onderzochte boom dat ze vastlegt. Vermeld daarom geen gegiste versies. [16]

**[Afleiding] Maak onderscheid tussen importeren en verspreiden.** Alleen een bibliotheek aanroepen vanuit eigen code maakt jouw hele script niet automatisch eigendom van die bibliotheekmaker. Een licentievermelding voor elke dependency is nuttig voor reproduceerbaarheid, maar een import alleen bewijst niet dat je die dependency meelevert. Bij letterlijk overgenomen broncode of gebundelde packages ontstaan de bijbehorende behouds- en verspreidingsverplichtingen.

Bij de gecontroleerde huidige roots van de vier Qiskit-projecten is geen rootbestand NOTICE aangetroffen. Dit vervangt niet de controle van de exacte overgenomen bestanden of meegeleverde distributie. Maak geen fictieve “IBM NOTICE” en neem geen copyrightjaartal uit een ander bestand over als vervanging voor de feitelijke bronheader.

Voor PQID is een bronrecord per afgeleid fragment wenselijk: repository, pad, commit, blob, toepasselijke licenties, behouden copyright/attribution, upstreambronnen en door PQID aangebrachte wijzigingen. De volledige standaardlicentietekst moet met de codecollectie beschikbaar zijn waar de licentie dat vereist; alleen een URL in metadata is daarvoor geen vervanging. Een academische bronvermelding is nuttig naast de wettelijke notices, maar geen vervanging ervan.

## 6 Engelse concepttekst voor een afgebakende vrijgave

**PUBLICATIECONCEPT. Bram Dobbelaar is als enige auteur van zijn runnerbijdragen bevestigd en heeft Apache-2.0 gekozen. De afzonderlijke upstreamvermeldingen blijven gelden. Er is nog niets gepubliceerd.** De onderstaande tekst is een scopeverklaring naast de ongewijzigde standaard Apache-2.0-tekst. Zij is geen nieuwe maatwerklicentie en geldt nu niet als toestemming.

### Concept voor LICENSE SCOPE

```text
Scope of the Apache License, Version 2.0

Bram Dobbelaar licenses only the copyrightable contributions that he owns
or is authorised to license in the following source file, including its
explanatory comments and docstrings:

Repository:
https://github.com/BramDo/onderzoek_blackhole_echo_status_2026-03-05_131816

Path:
files/quantum-math-lab/qiskit_black_hole_hardware_runner.py

Recorded Git blob:
30905b5b42a559f233527f0ea487f330cb6b1888

Source snapshot commit:
78e09c48ab25b3c6ebc3fed36c483123fc057a61

These contributions are licensed under the unmodified Apache License,
Version 2.0, whose full text accompanies this scope statement.

Rights in third-party source material remain with their respective
rights holders and remain subject to the applicable upstream terms.
This statement does not relicense that material.

The M3 calibration adapter in _build_m3_marginal_mitigator closely follows
the marginal-calibration implementation in Qiskit/qiskit-addon-mthree,
mthree/mitigation.py, at comparison commit
8402654566900aed11b64f625e18b49aefb902eb.
It is conservatively attributed as potentially adapted IBM/M3 material.
Its upstream Apache-2.0 terms and IBM 2021 copyright notice are retained.
This comparison commit is not asserted to be the exact version used
during development.

This scope does not include imported libraries, the separately stored
qiskit_black_hole_scrambling.py module, external PE-LiNN model source,
model checkpoints or weights, experimental datasets or job outputs,
figures, papers, README files, or other repository content.

The software licence imposes no field-of-use restriction.
This statement neither grants rights owned by third parties nor resolves
any separately applicable contractual obligations.

The grant applies to the identified recorded version from the date on
which the final licence notice is published. It does not certify that any
earlier use was authorised and does not automatically cover other files
or future versions.
```

Het herkomstregister vermeldt Bram Dobbelaar als enige auteur van de eigen runnerbijdragen, met AI als hulpmiddel. De mogelijke M3-adaptatie blijft afzonderlijk benoemd. De scope is beperkt tot de geregistreerde runner en haar opmerkingen; onbekende rechten van derden worden niet als Brams rechten gepresenteerd.

### Concept voor de bronheader

De enige auteurscredit is Bram Dobbelaar. De IBM-regel hieronder is een afzonderlijke upstreamvermelding voor het mogelijke M3-materiaal en geen credit als coauteur van de runner.

```python
# SPDX-FileCopyrightText: 2026 Bram Dobbelaar
# SPDX-License-Identifier: Apache-2.0
#
# Scope: Bram-controlled contributions in this runner, including comments
# and docstrings. See the accompanying scope and provenance statements.
#
# Potentially adapted M3 calibration material:
# (C) Copyright IBM 2021.
# Apache-2.0; see the upstream reference and modification description
# for _build_m3_marginal_mitigator.
```

Deze header is een voorgestelde commentaarwijziging en verandert de API-aanroepen niet. De runner gebruikt QuantumCircuit, Statevector en Runtime SamplerV2; hij bevat daarnaast oudere Runtime-fallbacks. De scramblingmodule importeert AerSimulator uit qiskit_aer. De licentiecontrole is geen bevestiging dat alle historische Runtime-fallbacks met iedere Qiskit-versie vanaf 2.1 werken. Er zijn geen circuits uitgevoerd of wetenschappelijke resultaten opnieuw gevalideerd.

Voor het mogelijke M3-blok moet de feitelijke upstreamheader behouden worden als adaptatie wordt bevestigd. De korte SPDX-header is dan een aanvulling, geen vervanging voor overgenomen notices. De Apache-vermelding en disclaimer moeten overeenkomstig de officiële toepassingstekst beschikbaar zijn. [6, 10]

### Concept voor het herkomstregister

```text
Component: _build_m3_marginal_mitigator
Provenance status: potential adaptation, conservatively attributed
Upstream: Qiskit/qiskit-addon-mthree, mthree/mitigation.py
Comparison commit: 8402654566900aed11b64f625e18b49aefb902eb
Comparison blob: 486105ee893f5abce0bc6006af45b8cf12506d69
Upstream file notice: (C) Copyright IBM 2021.
Upstream licence: Apache-2.0

Compared with the upstream marginal-calibration branch, this adapter
accepts already collected all-zero and all-one histograms, normalises
their bitstrings, populates an M3Mitigation object directly, and returns
calibration diagnostics. The exact checkout used during development
has not been established.

Companion-module provenance:
qiskit_black_hole_scrambling.py attributes the experiment to a shared
ChatGPT discussion. The original session and a passage-level record
of AI assistance have not been recovered.

Other runner contributions:
Sole credited author: Bram Dobbelaar.
Bram confirms that he developed the runner with assistance from
ChatGPT/Codex. Those systems are tools, not co-authors.
Chosen licence for Bram's own contributions: Apache-2.0.
Publication of the notice has not yet taken place.
```

**Voorgestelde bestandsindeling na een besluit:** een `LICENSES/Apache-2.0.txt` met de volledige ongewijzigde standaardtekst, een expliciete scopeverklaring en een herkomstregister. Pas de header alleen in het bevestigde bronbestand toe. Voeg geen algemene rootverklaring toe die alle repositoryinhoud zonder onderscheid Apache noemt.

De oude blob kan exact worden aangewezen in de nieuwe scopeverklaring, ook al verandert het invoegen van een header de hash van een nieuwe versie. Bewaar beide hashes in de licentieregistratie. De licentie wordt nu verleend voor het oude exemplaar; schrijf geen fictieve licentiedatum in het verleden.

Als alleen een beperkt aantal functies aantoonbaar van jou is, publiceer daarvoor een expliciet benoemde scope. Laat Elias het resterende bestand als onbevestigd behandelen totdat het eveneens is gecontroleerd.

## 7 Bronvermelding en Engels antwoord aan Elias

### Voorgestelde bronvermelding

Bronvermelding met Bram Dobbelaar als enige auteur, volgens zijn bevestiging:

```text
Dobbelaar, Bram. 2026.
qiskit_black_hole_hardware_runner.py.
BramDo/onderzoek_blackhole_echo_status_2026-03-05_131816.
Snapshot commit: 78e09c48ab25b3c6ebc3fed36c483123fc057a61.
Git blob: 30905b5b42a559f233527f0ea487f330cb6b1888.
Source:
https://github.com/BramDo/onderzoek_blackhole_echo_status_2026-03-05_131816/blob/78e09c48ab25b3c6ebc3fed36c483123fc057a61/files/quantum-math-lab/qiskit_black_hole_hardware_runner.py

Author: Bram Dobbelaar (sole credited author).
Development assistance: ChatGPT/Codex (tools, not co-authors).
Chosen software licence: Apache-2.0 for Bram's own contributions.
Licence notice publication: pending.
Retain separate applicable upstream notices.
```

Na publicatie worden de publicatiedatum en permanente link naar de licentienotice toegevoegd. De auteurscredit blijft uitsluitend Bram Dobbelaar. Laat Elias afgeleide PQID-fragmenten aan dit bronrecord koppelen. Een bronvermelding verplicht geen coauteurschap van toekomstige papers en suggereert geen validatie van de experimentele claims.

### Engels conceptantwoord met de bevestigde auteur en licentiekeuze

Dit antwoord is gereed als feitelijke tussenstand, maar is niet verstuurd.

> Hi Elias,
>
> Thank you for asking about the licence and provenance of this runner. I have reviewed the recorded file and its visible history. The current file still has Git blob 30905b5b42a559f233527f0ea487f330cb6b1888.
>
> I developed this runner with assistance from ChatGPT/Codex. Please credit Bram Dobbelaar as its sole author. ChatGPT/Codex was used as a development tool, not as a co-author. This authorship credit does not claim ownership of any underlying third-party material. The visible history records the file's import on 18 March 2026 and a substantial update on 22 March under my GitHub account.
>
> One specific point requires upstream attribution: _build_m3_marginal_mitigator closely follows the marginal-calibration logic in Qiskit/qiskit-addon-mthree/mthree/mitigation.py. I am treating this as a potential adaptation pending confirmation. A pre-existing comparison version is commit 8402654566900aed11b64f625e18b49aefb902eb, whose source file carries IBM's 2021 copyright notice and Apache-2.0 terms. This is a comparison reference, not a claim about the exact checkout originally used.
>
> The runner also imports Qiskit, qiskit-ibm-runtime, NumPy and PyTorch, optionally uses mthree, and can load an external PE-LiNN model. These components retain their own terms. The candidate PELINN-Q model repository carries an MIT notice naming paolodarold; I am not claiming ownership of that model source or granting rights to model weights.
>
> I have chosen the Apache License, Version 2.0 (SPDX: Apache-2.0), for my own contributions in this runner, including the corresponding comments and docstrings. The proposed file-scoped notice explicitly identifies your recorded blob. The notice has not yet been published; this draft is not itself a licence grant.
>
> For now, please keep the source record pending rather than treating this message as permission for adaptation or public redistribution. The proposed scope would exclude the companion module unless separately cleared, imported libraries, external models and checkpoints, experimental data, figures, papers and other repository files.
>
> Please use Bram Dobbelaar as the sole author in the source credit, together with the repository and path, snapshot commit 78e09c48ab25b3c6ebc3fed36c483123fc057a61 and the recorded blob. Preserve applicable third-party notices separately; they are not co-author credits for the runner. Please retain the source-specific software terms alongside any dataset-level licence.
>
> Best regards,
> Bram

### Engels conceptantwoord voor na publicatie

Niet gebruiken zolang een van de vierkante placeholders niet met een bevestigd feit kan worden ingevuld.

```text
Hi Elias,

I have now published a file-scoped Apache License, Version 2.0
(SPDX: Apache-2.0), notice for my own contributions in
files/quantum-math-lab/qiskit_black_hole_hardware_runner.py,
including its corresponding comments and docstrings.

The notice explicitly covers your recorded Git blob
30905b5b42a559f233527f0ea487f330cb6b1888:
[PERMANENT LICENCE NOTICE URL AND PUBLICATION DATE].

Please retain the following source credit:
Bram Dobbelaar, sole credited author. 2026.
qiskit_black_hole_hardware_runner.py.
BramDo/onderzoek_blackhole_echo_status_2026-03-05_131816.
Snapshot commit: 78e09c48ab25b3c6ebc3fed36c483123fc057a61.
Git blob: 30905b5b42a559f233527f0ea487f330cb6b1888.

The provenance record is available at [PERMANENT PROVENANCE URL].
It identifies my runner contributions and the separately attributed
possible M3 calibration adaptation. ChatGPT/Codex is acknowledged
solely as a development tool, not as a co-author.
The possible M3 calibration adaptation is separately attributed to its
upstream source under Apache-2.0 with the applicable IBM notice retained.

Imported libraries and any separately sourced code retain their own
terms. This notice does not cover the companion module unless expressly
listed, external PE-LiNN model source or checkpoints, experimental data,
figures, papers, or other repository files.

Subject to the applicable source licences and any separately applicable
obligations, the licensed contributions may be copied, adapted and
redistributed for dataset construction and used for model training and
evaluation. Please preserve the full required licence texts, applicable
notices, source traceability and modification notices in the release.

This notice does not establish PQID inclusion, imply endorsement, or
validate the experimental claims.

Best regards,
Bram
```

## 8 Vastgelegde keuzes en publicatiestatus

Op 11 oktober 2026 heeft Bram Dobbelaar bevestigd dat hij de runner zelf ontwikkelde met ChatGPT/Codex als hulpmiddel. Hij heeft Apache-2.0 gekozen voor zijn eigen bijdragen en expliciet gevraagd alleen hem als auteur te vermelden.

De definitieve voorgestelde auteurscredit is **Bram Dobbelaar**. ChatGPT/Codex wordt niet als auteur opgenomen. De afzonderlijke IBM/M3-, Qiskit- en PE-LiNN-bronvermeldingen blijven behouden waar van toepassing; zij maken deze partijen niet tot coauteurs van de runner.

De repository en het issue zijn ongewijzigd. Dit document bevat het concrete voorstel voor publicatie en het Engelse conceptantwoord. Er is nog geen licentienotice gepubliceerd of reactie aan Elias verstuurd. De oorspronkelijke opdracht vroeg om een voorstel; de gemaakte keuze is hier verwerkt zonder een aanvullende publicatiehandeling te veronderstellen.

De exacte historische AI-sessie, toepasselijke dienstvoorwaarden en feitelijke upstreamcheckout blijven niet volledig vastgesteld. Deze beperkingen blijven in het herkomstregister staan; ze worden niet voorgesteld als ontbrekende menselijke co-auteurs.

## Bronnen

Alle vermelde repositoryinhoud en upstreamlicenties zijn op 11 oktober 2026 geraadpleegd. Een vergelijking met een oudere commit is aangegeven waar beschikbaar.

1. [Elias' issue en exacte vraag](https://github.com/BramDo/onderzoek_blackhole_echo_status_2026-03-05_131816/issues/1).
2. [Runner in gecontroleerde snapshot](https://github.com/BramDo/onderzoek_blackhole_echo_status_2026-03-05_131816/blob/78e09c48ab25b3c6ebc3fed36c483123fc057a61/files/quantum-math-lab/qiskit_black_hole_hardware_runner.py).
3. [Eerste runnerimport](https://github.com/BramDo/onderzoek_blackhole_echo_status_2026-03-05_131816/commit/ac38bea0f30e23d505d179c3e75747f98c7befae) en [runneruitbreiding](https://github.com/BramDo/onderzoek_blackhole_echo_status_2026-03-05_131816/commit/c5e6c9e7c83b5f3dbc8e204400d822cbf44bbfeb).
4. [Scramblingmodule met ChatGPT-verwijzing](https://github.com/BramDo/onderzoek_blackhole_echo_status_2026-03-05_131816/blob/78e09c48ab25b3c6ebc3fed36c483123fc057a61/files/quantum-math-lab/qiskit_black_hole_scrambling.py).
5. [Paperbron met auteursveld](https://github.com/BramDo/onderzoek_blackhole_echo_status_2026-03-05_131816/blob/78e09c48ab25b3c6ebc3fed36c483123fc057a61/paper/main.tex).
6. [M3-vergelijkingsbron uit 2025](https://github.com/Qiskit/qiskit-addon-mthree/blob/8402654566900aed11b64f625e18b49aefb902eb/mthree/mitigation.py) en [bijbehorende licentie](https://github.com/Qiskit/qiskit-addon-mthree/blob/8402654566900aed11b64f625e18b49aefb902eb/LICENSE.txt).
7. [PELINN-Q-licentie op oudere commit](https://github.com/BramDo/PELINN-Q/blob/04a399f942058bf5cee761958b7d513982d848c2/LICENSE) en [modelbron](https://github.com/BramDo/PELINN-Q/blob/04a399f942058bf5cee761958b7d513982d848c2/src/model.py).
8. [Richtlijn 2009/24/EG, artikelen 1 en 2](https://eur-lex.europa.eu/eli/dir/2009/24/oj/eng).
9. [OpenAI Europe Terms of Use, Content en Using our Services](https://openai.com/policies/eu-terms-of-use/). De exacte historisch toepasselijke versie en dienst zijn niet vastgesteld.
10. [Apache License Version 2.0, artikelen 2–4 en toepassing](https://www.apache.org/licenses/LICENSE-2.0).
11. [MIT License, Open Source Initiative](https://opensource.org/license/mit).
12. [BSD 3-Clause, Open Source Initiative](https://opensource.org/license/bsd-3-clause).
13. [GPL-3.0-only, officiële SPDX-licentietekst](https://spdx.org/licenses/GPL-3.0-only.html).
14. [Creative Commons FAQ over softwarelicenties](https://creativecommons.org/faq/#can-i-apply-a-creative-commons-license-to-software).
15. [PQID README](https://github.com/Elias-Abebe-Gasparini/PQID-Dataset/blob/main/README.md) en [datasetlicentie](https://github.com/Elias-Abebe-Gasparini/PQID-Dataset/blob/main/LICENSE.md).
16. Upstreamlicenties: [Qiskit](https://github.com/Qiskit/qiskit/blob/main/LICENSE.txt), [Runtime](https://github.com/Qiskit/qiskit-ibm-runtime/blob/main/LICENSE.txt), [Aer](https://github.com/Qiskit/qiskit-aer/blob/main/LICENSE.txt), [M3](https://github.com/Qiskit/qiskit-addon-mthree/blob/main/LICENSE.txt), [NumPy](https://github.com/numpy/numpy/blob/main/LICENSE.txt) en [PyTorch](https://github.com/pytorch/pytorch/blob/main/LICENSE).
17. [GitHub over repositories zonder licentie en toepasselijke standaardrechten](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository).

