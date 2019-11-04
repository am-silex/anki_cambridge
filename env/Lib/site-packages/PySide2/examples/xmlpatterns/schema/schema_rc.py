# -*- coding: utf-8 -*-

# Resource object code
#
# Created: Thu Oct 31 23:22:25 2019
#      by: The Resource Compiler for PySide2 (Qt v5.13.2)
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore

qt_resource_data = b"\
\x00\x00\x015\
<\
contact>\x0d\x0a    <g\
ivenName>John</g\
ivenName>\x0d\x0a    <\
familyName>Doe</\
familyName>\x0d\x0a   \
 <birthdate>1977\
-12-25</birthdat\
e>\x0d\x0a    <homeAdd\
ress>\x0d\x0a        <\
street>Sandakerv\
eien 116</street\
>\x0d\x0a        <zipC\
ode>N-0550</zipC\
ode>\x0d\x0a        <c\
ity>Oslo</city>\x0d\
\x0a        <countr\
y>Norway</countr\
y>\x0d\x0a    </homeAd\
dress>\x0d\x0a</contac\
t>\x0d\x0a\
\x00\x00\x01\xc8\
<\
order>\x0d\x0a    <cus\
tomerId>194223</\
customerId>\x0d\x0a   \
 <article>\x0d\x0a    \
    <articleId>2\
2242</articleId>\
\x0d\x0a        <count\
>5</count>\x0d\x0a    \
</article>\x0d\x0a    \
<article>\x0d\x0a     \
   <articleId>32\
372</articleId>\x0d\
\x0a        <count>\
12</count>\x0d\x0a    \
    <comment>wit\
hout stripes</co\
mment>\x0d\x0a    </ar\
ticle>\x0d\x0a    <art\
icle>\x0d\x0a        <\
articleId>23649<\
/articleId>\x0d\x0a   \
     <count>2</c\
ount>\x0d\x0a    </art\
icle>\x0d\x0a    <deli\
veryDate>2009-01\
-23</deliveryDat\
e>\x0d\x0a    <payed>t\
rue</payed>\x0d\x0a</o\
rder>\x0d\x0a\
\x00\x00\x03~\
<\
?xml version=\x221.\
0\x22?>\x0d\x0a<xsd:schem\
a xmlns:xsd=\x22htt\
p://www.w3.org/2\
001/XMLSchema\x22>\x0d\
\x0a\x0d\x0a    <xsd:elem\
ent name=\x22order\x22\
>\x0d\x0a        <xsd:\
complexType>\x0d\x0a  \
          <xsd:s\
equence>\x0d\x0a      \
          <xsd:e\
lement name=\x22cus\
tomerId\x22 type=\x22x\
sd:positiveInteg\
er\x22/>\x0d\x0a         \
       <xsd:elem\
ent name=\x22articl\
e\x22 type=\x22article\
Type\x22 maxOccurs=\
\x22unbounded\x22/>\x0d\x0a \
               <\
xsd:element name\
=\x22deliveryDate\x22 \
type=\x22xsd:date\x22/\
>\x0d\x0a             \
   <xsd:element \
name=\x22payed\x22 typ\
e=\x22xsd:boolean\x22/\
>\x0d\x0a            <\
/xsd:sequence>\x0d\x0a\
        </xsd:co\
mplexType>\x0d\x0a    \
</xsd:element>\x0d\x0a\
\x0d\x0a    <xsd:compl\
exType name=\x22art\
icleType\x22>\x0d\x0a    \
    <xsd:sequenc\
e>\x0d\x0a            \
<xsd:element nam\
e=\x22articleId\x22 ty\
pe=\x22xsd:positive\
Integer\x22/>\x0d\x0a    \
        <xsd:ele\
ment name=\x22count\
\x22 type=\x22xsd:posi\
tiveInteger\x22/>\x0d\x0a\
            <xsd\
:element name=\x22c\
omment\x22 type=\x22xs\
d:string\x22 minOcc\
urs=\x220\x22/>\x0d\x0a     \
   </xsd:sequenc\
e>\x0d\x0a    </xsd:co\
mplexType>\x0d\x0a\x0d\x0a</\
xsd:schema>\x0d\x0a\
\x00\x00\x02c\
<\
recipe>\x0d\x0a    <ti\
tle>Cheese on To\
ast</title>\x0d\x0a   \
 <ingredient nam\
e=\x22Bread\x22 quanti\
ty=\x222\x22 unit=\x22sli\
ces\x22/>\x0d\x0a    <ing\
redient name=\x22Ch\
eese\x22 quantity=\x22\
2\x22 unit=\x22slices\x22\
/>\x0d\x0a    <time qu\
antity=\x223\x22 unit=\
\x22days\x22/>\x0d\x0a    <m\
ethod>\x0d\x0a        \
<step>1. Slice t\
he bread and che\
ese.</step>\x0d\x0a   \
     <step>2. Gr\
ill one side of \
each slice of br\
ead.</step>\x0d\x0a   \
     <step>3. Tu\
rn over the brea\
d and place a sl\
ice of cheese on\
 each piece.</st\
ep>\x0d\x0a        <st\
ep>4. Grill unti\
l the cheese has\
 started to melt\
.</step>\x0d\x0a      \
  <step>5. Serve\
 and enjoy!</ste\
p>\x0d\x0a    </method\
>\x0d\x0a    <comment>\
Tell your friend\
s about it!</com\
ment>\x0d\x0a</recipe>\
\x0d\x0a\
\x00\x00\x06-\
<\
?xml version=\x221.\
0\x22?>\x0d\x0a<xsd:schem\
a xmlns:xsd=\x22htt\
p://www.w3.org/2\
001/XMLSchema\x22>\x0d\
\x0a\x0d\x0a    <xsd:elem\
ent name=\x22recipe\
\x22>\x0d\x0a        <xsd\
:complexType>\x0d\x0a \
           <xsd:\
sequence>\x0d\x0a     \
           <xsd:\
element name=\x22ti\
tle\x22 type=\x22xsd:s\
tring\x22/>\x0d\x0a      \
          <xsd:e\
lement name=\x22ing\
redient\x22 type=\x22i\
ngredientType\x22 m\
axOccurs=\x22unboun\
ded\x22/>\x0d\x0a        \
        <xsd:ele\
ment name=\x22time\x22\
 type=\x22timeType\x22\
/>\x0d\x0a            \
    <xsd:element\
 name=\x22method\x22>\x0d\
\x0a               \
     <xsd:comple\
xType>\x0d\x0a        \
                \
<xsd:sequence>\x0d\x0a\
                \
            <xsd\
:element name=\x22s\
tep\x22 type=\x22xsd:s\
tring\x22 maxOccurs\
=\x22unbounded\x22/>\x0d\x0a\
                \
        </xsd:se\
quence>\x0d\x0a       \
             </x\
sd:complexType>\x0d\
\x0a               \
 </xsd:element>\x0d\
\x0a            </x\
sd:sequence>\x0d\x0a  \
      </xsd:comp\
lexType>\x0d\x0a    </\
xsd:element>\x0d\x0a\x0d\x0a\
    <xsd:complex\
Type name=\x22ingre\
dientType\x22>\x0d\x0a   \
     <xsd:attrib\
ute name=\x22name\x22 \
type=\x22xsd:string\
\x22/>\x0d\x0a        <xs\
d:attribute name\
=\x22quantity\x22 type\
=\x22xsd:positiveIn\
teger\x22/>\x0d\x0a      \
  <xsd:attribute\
 name=\x22unit\x22 typ\
e=\x22xsd:string\x22/>\
\x0d\x0a    </xsd:comp\
lexType>\x0d\x0a\x0d\x0a    \
<xsd:complexType\
 name=\x22timeType\x22\
>\x0d\x0a        <xsd:\
attribute name=\x22\
quantity\x22 type=\x22\
xsd:positiveInte\
ger\x22/>\x0d\x0a        \
<xsd:attribute n\
ame=\x22unit\x22>\x0d\x0a   \
         <xsd:si\
mpleType>\x0d\x0a     \
           <xsd:\
restriction base\
=\x22xsd:string\x22>\x0d\x0a\
                \
    <xsd:enumera\
tion value=\x22seco\
nds\x22/>\x0d\x0a        \
            <xsd\
:enumeration val\
ue=\x22minutes\x22/>\x0d\x0a\
                \
    <xsd:enumera\
tion value=\x22hour\
s\x22/>\x0d\x0a          \
      </xsd:rest\
riction>\x0d\x0a      \
      </xsd:simp\
leType>\x0d\x0a       \
 </xsd:attribute\
>\x0d\x0a    </xsd:com\
plexType>\x0d\x0a\x0d\x0a</x\
sd:schema>\x0d\x0a\
\x00\x00\x022\
<\
recipe>\x0d\x0a    <ti\
tle>Cheese on To\
ast</title>\x0d\x0a   \
 <ingredient nam\
e=\x22Bread\x22 quanti\
ty=\x222\x22 unit=\x22sli\
ces\x22/>\x0d\x0a    <ing\
redient name=\x22Ch\
eese\x22 quantity=\x22\
2\x22 unit=\x22slices\x22\
/>\x0d\x0a    <time qu\
antity=\x223\x22 unit=\
\x22minutes\x22/>\x0d\x0a   \
 <method>\x0d\x0a     \
   <step>1. Slic\
e the bread and \
cheese.</step>\x0d\x0a\
        <step>2.\
 Grill one side \
of each slice of\
 bread.</step>\x0d\x0a\
        <step>3.\
 Turn over the b\
read and place a\
 slice of cheese\
 on each piece.<\
/step>\x0d\x0a        \
<step>4. Grill u\
ntil the cheese \
has started to m\
elt.</step>\x0d\x0a   \
     <step>5. Se\
rve and enjoy!</\
step>\x0d\x0a    </met\
hod>\x0d\x0a</recipe>\x0d\
\x0a\
\x00\x00\x03\xd4\
<\
?xml version=\x221.\
0\x22?>\x0d\x0a<xsd:schem\
a xmlns:xsd=\x22htt\
p://www.w3.org/2\
001/XMLSchema\x22>\x0d\
\x0a\x0d\x0a    <xsd:elem\
ent name=\x22contac\
t\x22>\x0d\x0a        <xs\
d:complexType>\x0d\x0a\
            <xsd\
:sequence>\x0d\x0a    \
            <xsd\
:element name=\x22g\
ivenName\x22 type=\x22\
xsd:string\x22/>\x0d\x0a \
               <\
xsd:element name\
=\x22familyName\x22 ty\
pe=\x22xsd:string\x22/\
>\x0d\x0a             \
   <xsd:element \
name=\x22birthdate\x22\
 type=\x22xsd:date\x22\
 minOccurs=\x220\x22/>\
\x0d\x0a              \
  <xsd:element n\
ame=\x22homeAddress\
\x22 type=\x22address\x22\
/>\x0d\x0a            \
    <xsd:element\
 name=\x22workAddre\
ss\x22 type=\x22addres\
s\x22 minOccurs=\x220\x22\
/>\x0d\x0a            \
</xsd:sequence>\x0d\
\x0a        </xsd:c\
omplexType>\x0d\x0a   \
 </xsd:element>\x0d\
\x0a\x0d\x0a    <xsd:comp\
lexType name=\x22ad\
dress\x22>\x0d\x0a       \
 <xsd:sequence>\x0d\
\x0a            <xs\
d:element name=\x22\
street\x22 type=\x22xs\
d:string\x22/>\x0d\x0a   \
         <xsd:el\
ement name=\x22zipC\
ode\x22 type=\x22xsd:s\
tring\x22/>\x0d\x0a      \
      <xsd:eleme\
nt name=\x22city\x22 t\
ype=\x22xsd:string\x22\
/>\x0d\x0a            \
<xsd:element nam\
e=\x22country\x22 type\
=\x22xsd:string\x22/>\x0d\
\x0a        </xsd:s\
equence>\x0d\x0a    </\
xsd:complexType>\
\x0d\x0a\x0d\x0a</xsd:schema\
>\x0d\x0a\
\x00\x00\x01(\
<\
contact>\x0d\x0a    <g\
ivenName>John</g\
ivenName>\x0d\x0a    <\
familyName>Doe</\
familyName>\x0d\x0a   \
 <title>Prof.</t\
itle>\x0d\x0a    <work\
Address>\x0d\x0a      \
  <street>Sandak\
erveien 116</str\
eet>\x0d\x0a        <z\
ipCode>N-0550</z\
ipCode>\x0d\x0a       \
 <city>Oslo</cit\
y>\x0d\x0a        <cou\
ntry>Norway</cou\
ntry>\x0d\x0a    </wor\
kAddress>\x0d\x0a</con\
tact>\x0d\x0a\
\x00\x00\x01;\
<\
order>\x0d\x0a    <cus\
tomerId>234219</\
customerId>\x0d\x0a   \
 <article>\x0d\x0a    \
    <articleId>2\
1692</articleId>\
\x0d\x0a        <count\
>3</count>\x0d\x0a    \
</article>\x0d\x0a    \
<article>\x0d\x0a     \
   <articleId>24\
749</articleId>\x0d\
\x0a        <count>\
9</count>\x0d\x0a    <\
/article>\x0d\x0a    <\
deliveryDate>200\
9-01-23</deliver\
yDate>\x0d\x0a    <pay\
ed>yes</payed>\x0d\x0a\
</order>\x0d\x0a\
"

qt_resource_name = b"\
\x00\x0e\
\x00vJ\x1c\
\x00i\
\x00n\x00s\x00t\x00a\x00n\x00c\x00e\x00_\x000\x00.\x00x\x00m\x00l\
\x00\x0e\
\x00rJ\x1c\
\x00i\
\x00n\x00s\x00t\x00a\x00n\x00c\x00e\x00_\x004\x00.\x00x\x00m\x00l\
\x00\x0c\
\x08\x16\x87\xf4\
\x00s\
\x00c\x00h\x00e\x00m\x00a\x00_\x002\x00.\x00x\x00s\x00d\
\x00\x0e\
\x00sJ\x1c\
\x00i\
\x00n\x00s\x00t\x00a\x00n\x00c\x00e\x00_\x003\x00.\x00x\x00m\x00l\
\x00\x0c\
\x08\x13\x87\xf4\
\x00s\
\x00c\x00h\x00e\x00m\x00a\x00_\x001\x00.\x00x\x00s\x00d\
\x00\x0e\
\x00pJ\x1c\
\x00i\
\x00n\x00s\x00t\x00a\x00n\x00c\x00e\x00_\x002\x00.\x00x\x00m\x00l\
\x00\x0c\
\x08\x10\x87\xf4\
\x00s\
\x00c\x00h\x00e\x00m\x00a\x00_\x000\x00.\x00x\x00s\x00d\
\x00\x0e\
\x00yJ\x1c\
\x00i\
\x00n\x00s\x00t\x00a\x00n\x00c\x00e\x00_\x001\x00.\x00x\x00m\x00l\
\x00\x0e\
\x00uJ\x1c\
\x00i\
\x00n\x00s\x00t\x00a\x00n\x00c\x00e\x00_\x005\x00.\x00x\x00m\x00l\
"

qt_resource_struct = b"\
\x00\x00\x00\x00\x00\x02\x00\x00\x00\x09\x00\x00\x00\x01\
\x00\x00\x00\xa2\x00\x00\x00\x00\x00\x01\x00\x00\x0f\x1f\
\x00\x00\x00\x22\x00\x00\x00\x00\x00\x01\x00\x00\x019\
\x00\x00\x00b\x00\x00\x00\x00\x00\x01\x00\x00\x06\x87\
\x00\x00\x01\x04\x00\x00\x00\x00\x00\x01\x00\x00\x16Y\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\
\x00\x00\x00\xe2\x00\x00\x00\x00\x00\x01\x00\x00\x15-\
\x00\x00\x00\xc4\x00\x00\x00\x00\x00\x01\x00\x00\x11U\
\x00\x00\x00\x84\x00\x00\x00\x00\x00\x01\x00\x00\x08\xee\
\x00\x00\x00D\x00\x00\x00\x00\x00\x01\x00\x00\x03\x05\
"

def qInitResources():
    QtCore.qRegisterResourceData(0x01, qt_resource_struct, qt_resource_name, qt_resource_data)

def qCleanupResources():
    QtCore.qUnregisterResourceData(0x01, qt_resource_struct, qt_resource_name, qt_resource_data)

qInitResources()
