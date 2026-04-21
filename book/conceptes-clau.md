# Conceptes clau per a lectors no tècnics

Aquest annex recull, en forma breu, uns quants conceptes del món de la producció de programari que apareixen de manera implícita en aquest document i que expliquen per què certes decisions aparentment tècniques són, en realitat, decisions organitzatives i polítiques. Serveix de suport per als lectors que no es dediquen professionalment al desenvolupament ni a la gestió de serveis digitals.

## Llei de Conway

Observació formulada l'any 1967 per Melvin Conway: *qualsevol organització que dissenya un sistema acaba produint un disseny que reprodueix l'estructura de comunicació interna de l'organització*. Aplicada al sector públic, significa que la forma de l'organigrama determina la forma dels serveis digitals. Departaments que no es parlen produeixen serveis que no es parlen, per bona que sigui la qualitat tècnica de cada peça. Per això qualsevol estratègia seriosa d'administració digital, tard o d'hora, acaba tocant l'organització dels equips. [Més informació: [Wikipedia](https://ca.wikipedia.org/wiki/Llei_de_Conway)]

## Equips per cas d'ús

Alternativa al model d'organització per funcions o per departaments. Un equip per cas d'ús és estable, petit i multidisciplinari (enginyeria, disseny, gestió de producte, coneixement de domini) i és responsable d'una experiència concreta de la persona usuària de principi a fi. Exemple: en lloc d'un equip de digitalització al Departament d'Economia i un altre al de Treball, un sol equip és responsable del tràmit "donar d'alta una empresa" —des del formulari inicial fins a l'alta a la Seguretat Social—, inclosos els traspassos entre ministeris i les excepcions legals. És el model que han adoptat els referents internacionals (GDS, USDS, DINUM) i la pràctica totalitat de les empreses de producte digital que han escalat amb èxit.

## Dogfooding

Pràctica originada a Microsoft als anys vuitanta, agafada del proverbi anglès *eat your own dog food*: exigir als equips que construeixen un producte que l'utilitzin ells mateixos en la seva feina diària abans d'oferir-lo als usuaris finals. Al sector públic té un apalancament especialment alt: si els funcionaris que dissenyen el formulari d'autoliquidació han de presentar la seva pròpia declaració amb aquell mateix formulari, els defectes deixen de ser una estadística abstracta i passen a ser una molèstia personal. És una mesura de cost pràcticament zero i sistemàticament ignorada.

## Producte i projecte

Dos models de gestió de la tecnologia. Un **projecte** té un principi, un final i un lliurable acordat per contracte; quan s'acaba, l'equip es dissol i la responsabilitat operativa passa a algú altre o desapareix. Un **producte** és un servei que es manté, s'amida i evoluciona al llarg dels anys en funció de l'ús real, amb un responsable estable i mètriques contínues de resultat. L'administració pública tradicional contracta tecnologia en mode projecte (plec, lliurable, recepció, final); les organitzacions digitals la gestionen en mode producte. La diferència és decisiva: el projecte optimitza el compliment del plec, el producte optimitza el resultat per a l'usuari.

## Codi obert

Programari el codi font del qual es publica amb una llicència que permet a qualsevol persona consultar-lo, modificar-lo, redistribuir-lo i reutilitzar-lo. Al sector públic no és una posició ideològica: és una decisió de gestió que redueix la dependència de proveïdors, permet l'auditoria independent, facilita la reutilització entre administracions i converteix ciutadans i empreses en contribuïdors potencials dels serveis públics. Una administració que publica el seu codi obre, de retruc, un canal de col·laboració amb el teixit local que el model tancat bloqueja per construcció.

## Interfície de programació (API)

Mecanisme pel qual un servei digital exposa les seves funcions a altres serveis o programes de manera estable, documentada i automatitzable. Quan l'administració publica dades "via API", vol dir que un programa (una aplicació de tercers, un assistent virtual, un servei municipal) pot consultar-les i actualitzar-les directament, sense que una persona hagi d'entrar en un portal i copiar-les a mà. Les API són la diferència entre una administració que exposa pàgines web per a humans i una administració que es pot integrar amb la resta de l'ecosistema digital.
