grammar WURCS;

start:
    WURCS_HEAD FSLASH whatever FSLASH mono* FSLASH order FSLASH tree?;
whatever:
    single_num  (COMMA single_num)*;
mono:
    LBRACE (A | D | H | M | U | UU | X | single_num)* (DASH specs)? (UNDERSCORE specs)* RBRACE;
order:
    num (DASH num)*;
tree:
    pos DASH pos (UNDERSCORE pos DASH pos);
specs:
    num orient
    | num DASH num
    | num ASTERISK sidechain;
sidechain:
    organics* (FSLASH num EQ organics)*;
organics:
    NITROGEN | CARBON | OXYGEN | FG;
pos:
    (A | B) num;
orient:
    X | A | B;
single_num:
    ZERO | DIGIT;
num:
    DIGIT single_num*;

// Token
WURCS_HEAD:
    'WURCS=2.0';
FSLASH:
    '/';
FREEEND:
    'freeEnd';
REDEND:
    'redEnd';
SAC:
    'Glc' | 'Man' | 'Gal' | 'Gul' | 'Alt' | 'All' | 'Tal' | 'Ido' | 'Qui' | 'Rha' | 'Fuc' | 'Oli' | 'Tyv'
    | 'Abe' | 'Par' | 'Dig' | 'Col' | 'Ara' | 'Lyx' | 'Xyl' | 'Rib' | 'Kdn' | 'Neu' | 'Sia' | 'Pse' | 'Leg' | 'Aci'
    | 'Bac' | 'Kdo' | 'Dha' | 'Mur' | 'Api' | 'Fru' | 'Tag' | 'Sor' | 'Psi' | 'Ery' | 'Thre' | 'Rul' | 'Xul' | 'Unk'
    | 'Ace' | 'Aco' | 'Asc' | 'Fus' | 'Ins' | 'Ko' | 'Pau' | 'Per'| 'Sed' | 'Sug' | 'Vio' | 'Xlu' | 'Yer' | 'Erwiniose';
CARBON:
	'C';
NITROGEN:
    'N';
OXYGEN:
    'O';
FG:
    'Ceroplastic' | 'Lacceroic' | '3oxoMyr' | 'Psyllic' | 'Geddic' | 'Alloc' | 'Allyl' | 'Phthi' | 'TBDPS' | 'aLnn'
    | 'ClAc' | 'Coum' | 'eSte' | 'Fmoc' | 'gLnn' | 'HSer' | 'Pico' | 'Prop' | 'TIPS' | 'triN' | 'Troc' | 'Ach' | 'Aep'
    | 'Ala' | 'Ang' | 'Asp' | 'Beh' | 'Boc' | 'But' | 'Cbz' | 'Cct' | 'Cer' | 'Cet' | 'Cho' | 'cHx' | 'Cin' | 'Crt'
    | 'Cys' | 'DCA' | 'Dce' | 'Dco' | 'Dec' | 'Dhp' | 'DMT' | 'Dod' | 'Etg' | 'Etn' | 'EtN' | 'Fer' | 'Glu' | 'Gly'
    | 'Gro' | 'Hpo' | 'Hse' | 'Hxo' | 'Lac' | 'Lau' | 'Leu' | 'Lev' | 'Lin' | 'Lys' | 'Mal' | 'Mar' | 'Mel' | 'MMT'
    | 'MOM' | 'Mon' | 'Myr' | 'NAP' | 'Ner' | 'Nno' | 'Non' | 'Oco' | 'Ole' | 'oNB' | 'Orn' | 'Pam' | 'Pic' | 'Piv'
    | 'PMB' | 'PMP' | 'Poc' | 'Pro' | 'Pyr' | 'Ser' | 'Sin' | 'Ste' | 'TBS' | 'tBu' | 'TCA' | 'TES' | 'TFA' | 'THP'
    | 'Thr' | 'Tig' | 'TMS' | 'Udo' | 'Ulo' | 'ulo' | 'Und' | 'Vac' | 'Ac' | 'Al' | 'Am' | 'Bn' | 'Br' | 'Bu' | 'Bz'
    | 'Cl' | 'Cm' | 'DD' | 'DL' | 'en' | 'Et' | 'Fo' | 'Gc' | 'Hp' | 'Hx' | 'LD' | 'LL' | 'Me' | 'Nn' | 'Ns'
    | 'Oc' | 'Pe' | 'Ph' | 'Pp' | 'Pr' | 'Tf' | 'Tr' | 'Ts' | 'Vl' | 'A' | 'F' | 'I' | 'S' | 'P';
ANHYDRO:
    'Anhydro';
HEAD:
    '0d';
HEADD:
    'D' | 'L';
END:
	'ulosaric' | 'ulosonic' | 'uronic' | 'onic' | 'aric' | 'ol';
COUNT:
    'Hep' | 'Hex' | 'Oct' | 'Pen' | 'Suc';
TYPE:
    'a' | 'b';
RING:
    'p' | 'f';
DIGIT:
    ('1'..'9');
ZERO:
    '0';
AT:
    '@';
COMMA:
	',';
SEMICOLON: 
    ';';
DOUBLEDASH: 
    '--';
DASH:
	'-';
LPAR:
	'(';
RPAR:
	')';
LBRACE:
	'[';
RBRACE:
	']';
LBRACK:
    '{';
RBRACK:
    '}';
AI:
	'ai';
A:
	'a';
B:
    'b';
C:
	'c';
D:
	'd';
E:
	'e';
H:
    'h';
M:
    'm';
T:
    't';
I:
	'i';
U:
    'u';
UU:
    'U';
X:
    'x';
EQ:
	'=';
UNDERSCORE:
    '_';
DOLLAR:
    '$';
HASH:
    '#';
SPACE:
    ' ';
ASTERISK:
    '*';
QMARK:
	'?';

// antlr -Dlanguage=Python3 IUPAC.g4
