'''
2024 Bjoern Annighoefer
'''

from ..domain import Domain
from ..command import Cmp
from ..query import His, Obj
from ..value import BOL,U32,I32,I64,F32,LST,NON,STR

def CreateWarehouseM2Model(domain:Domain, sessionId:str=None)->Obj:
    """Create warehouse meta-model as given in the getting started section
    
                                                              _______________
         ___________              _______________            |    Product    |
        | Warehouse | categories |   Category    |  products |---------------|
        |-----------|<>--------->|---------------|<>-------->| name : string |
        |           |           *| name : string |          *| price : real  |
        |___________|        o-->|_______________|<>-o       | sells : int   |
                             |  *                    |       |_______________|
                             o-----------------------o
                                   categories
        
    """
    #the following is generated form eoq2's example warehouse.ecore
    cmd = Cmp().Crt(STR('*M2MODEL'),U32(1),LST([STR('warehouse')]),NON(),LST([]),resName='o0')\
               .Crt(STR('*M2CLASS'),U32(1),LST([STR('Warehouse'),BOL(False),His(STR('o0'))]),NON(),LST([]),resName='o1')\
               .Crt(STR('*M2CLASS'),U32(1),LST([STR('Category'),BOL(False),His(STR('o0'))]),NON(),LST([]),resName='o2')\
               .Crt(STR('*M2CLASS'),U32(1),LST([STR('Product'),BOL(False),His(STR('o0'))]),NON(),LST([]),resName='o3')\
               .Crt(STR('*M2COMPOSITION'),U32(1),LST([STR('categories'),His(STR('o1')),His(STR('o2')),I64(-1),BOL(False)]),NON(),LST([]),resName='o4')\
               .Crt(STR('*M2ATTRIBUTE'),U32(1),LST([STR('name'),His(STR('o2')),STR('*STR'),I64(1),NON(),NON()]),NON(),LST([]),resName='o5')\
               .Crt(STR('*M2COMPOSITION'),U32(1),LST([STR('categories'),His(STR('o2')),His(STR('o2')),I64(-1),BOL(False)]),NON(),LST([]),resName='o6')\
               .Crt(STR('*M2COMPOSITION'),U32(1),LST([STR('products'),His(STR('o2')),His(STR('o3')),I64(-1),BOL(False)]),NON(),LST([]),resName='o7')\
               .Crt(STR('*M2ATTRIBUTE'),U32(1),LST([STR('name'),His(STR('o3')),STR('*STR'),I64(1),NON(),NON()]),NON(),LST([]),resName='o8')\
               .Crt(STR('*M2ATTRIBUTE'),U32(1),LST([STR('price'),His(STR('o3')),STR('*F32'),I64(1),NON(),NON()]),NON(),LST([]),resName='o9')\
               .Crt(STR('*M2ATTRIBUTE'),U32(1),LST([STR('sells'),His(STR('o3')),STR('*I32'),I64(1),NON(),NON()]),NON(),LST([]),resName='o10')
    #execute the command on the domain
    res = domain.Do(cmd,sessionId)
    m1model = res[0]
    return m1model
          
def CreateWarehouseM1Model(domain:Domain, sessionId=None)->Obj:
    """Create warehouse user model with the following content: 
    
        <warehouse>
          <categories name="food">
            <categories name="fresh">
              <categories name="fruit">
                <products name="Apple" sells="400" price="0.25"/>
                <products name="Banana" sells="1" price="0.35"/>
                <products name="Orange" sells="20" price="0.45"/>
                <products name="Melon" sells="2" price="1.1"/>
              </categories>
              <categories name="vegetables">
                <products name="Cucumber" sells="4" price="0.5"/>
                <products name="Lettuce" sells="2" price="0.8"/>
              </categories>
              <categories name="milk">
                <products name="Cream" sells="300" price="0.5"/>
                <products name="Milk" sells="700" price="0.6"/>
                <categories name="cheese">
                  <products name="Goat Cheese" price="5.0"/>
                  <products name="Gouda" sells="100" price="2.0"/>
                </categories>
              </categories>
            </categories>
            <categories name="drinks">
              <products name="Coffee" sells="100" price="2.0"/>
              <products name="Hot Chocolate" sells="1" price="2.5"/>
              <categories name="lemonade">
                <products name="Coke" sells="1000" price="1.0"/>
                <products name="Energy Drink" price="10.0"/>
              </categories>
            </categories>
          </categories>
        </warehouse>
    
    """
    #the following is generated form eoq2's example GeneralsStore.warehouse
    cmd = Cmp().Crt(STR('*M1MODEL'),U32(1),LST([STR('warehouse'),STR('m1model')]),NON(),LST([]),resName='o0')\
               .Crt(STR('*M1OBJECT'),U32(1),LST([STR('warehouse__Warehouse'),His(STR('o0')),NON()]),NON(),LST([]),resName='o1')\
               .Crt(STR('*M1OBJECT'),U32(1),LST([STR('warehouse__Category'),His(STR('o0')),STR('food')]),NON(),LST([]),resName='o2')\
               .Crt(STR('*M1ATTRIBUTE'),U32(1),LST([STR('name'),His(STR('o2')),STR('food')]),NON(),LST([]))\
               .Crt(STR('*M1OBJECT'),U32(1),LST([STR('warehouse__Category'),His(STR('o0')),STR('fresh')]),NON(),LST([]),resName='o3')\
               .Crt(STR('*M1ATTRIBUTE'),U32(1),LST([STR('name'),His(STR('o3')),STR('fresh')]),NON(),LST([]))\
               .Crt(STR('*M1OBJECT'),U32(1),LST([STR('warehouse__Category'),His(STR('o0')),STR('fruit')]),NON(),LST([]),resName='o4')\
               .Crt(STR('*M1ATTRIBUTE'),U32(1),LST([STR('name'),His(STR('o4')),STR('fruit')]),NON(),LST([]))\
               .Crt(STR('*M1OBJECT'),U32(1),LST([STR('warehouse__Product'),His(STR('o0')),STR('Apple')]),NON(),LST([]),resName='o5')\
               .Crt(STR('*M1ATTRIBUTE'),U32(1),LST([STR('name'),His(STR('o5')),STR('Apple')]),NON(),LST([]))\
               .Crt(STR('*M1ATTRIBUTE'),U32(1),LST([STR('price'),His(STR('o5')),F32(0.250000)]),NON(),LST([]))\
               .Crt(STR('*M1ATTRIBUTE'),U32(1),LST([STR('sells'),His(STR('o5')),I32(400)]),NON(),LST([]))\
               .Crt(STR('*M1COMPOSITION'),U32(1),LST([STR('products'),His(STR('o4')),His(STR('o5'))]),NON(),LST([]))\
               .Crt(STR('*M1OBJECT'),U32(1),LST([STR('warehouse__Product'),His(STR('o0')),STR('Banana')]),NON(),LST([]),resName='o6')\
               .Crt(STR('*M1ATTRIBUTE'),U32(1),LST([STR('name'),His(STR('o6')),STR('Banana')]),NON(),LST([]))\
               .Crt(STR('*M1ATTRIBUTE'),U32(1),LST([STR('price'),His(STR('o6')),F32(0.350000)]),NON(),LST([]))\
               .Crt(STR('*M1ATTRIBUTE'),U32(1),LST([STR('sells'),His(STR('o6')),I32(1)]),NON(),LST([]))\
               .Crt(STR('*M1COMPOSITION'),U32(1),LST([STR('products'),His(STR('o4')),His(STR('o6'))]),NON(),LST([]))\
               .Crt(STR('*M1OBJECT'),U32(1),LST([STR('warehouse__Product'),His(STR('o0')),STR('Orange')]),NON(),LST([]),resName='o7')\
               .Crt(STR('*M1ATTRIBUTE'),U32(1),LST([STR('name'),His(STR('o7')),STR('Orange')]),NON(),LST([]))\
               .Crt(STR('*M1ATTRIBUTE'),U32(1),LST([STR('price'),His(STR('o7')),F32(0.450000)]),NON(),LST([]))\
               .Crt(STR('*M1ATTRIBUTE'),U32(1),LST([STR('sells'),His(STR('o7')),I32(20)]),NON(),LST([]))\
               .Crt(STR('*M1COMPOSITION'),U32(1),LST([STR('products'),His(STR('o4')),His(STR('o7'))]),NON(),LST([]))\
               .Crt(STR('*M1OBJECT'),U32(1),LST([STR('warehouse__Product'),His(STR('o0')),STR('Melon')]),NON(),LST([]),resName='o8')\
               .Crt(STR('*M1ATTRIBUTE'),U32(1),LST([STR('name'),His(STR('o8')),STR('Melon')]),NON(),LST([]))\
               .Crt(STR('*M1ATTRIBUTE'),U32(1),LST([STR('price'),His(STR('o8')),F32(1.100000)]),NON(),LST([]))\
               .Crt(STR('*M1ATTRIBUTE'),U32(1),LST([STR('sells'),His(STR('o8')),I32(2)]),NON(),LST([]))\
               .Crt(STR('*M1COMPOSITION'),U32(1),LST([STR('products'),His(STR('o4')),His(STR('o8'))]),NON(),LST([]))\
               .Crt(STR('*M1COMPOSITION'),U32(1),LST([STR('categories'),His(STR('o3')),His(STR('o4'))]),NON(),LST([]))\
               .Crt(STR('*M1OBJECT'),U32(1),LST([STR('warehouse__Category'),His(STR('o0')),STR('vegetables')]),NON(),LST([]),resName='o9')\
               .Crt(STR('*M1ATTRIBUTE'),U32(1),LST([STR('name'),His(STR('o9')),STR('vegetables')]),NON(),LST([]))\
               .Crt(STR('*M1OBJECT'),U32(1),LST([STR('warehouse__Product'),His(STR('o0')),STR('Cucumber')]),NON(),LST([]),resName='o10')\
               .Crt(STR('*M1ATTRIBUTE'),U32(1),LST([STR('name'),His(STR('o10')),STR('Cucumber')]),NON(),LST([]))\
               .Crt(STR('*M1ATTRIBUTE'),U32(1),LST([STR('price'),His(STR('o10')),F32(0.500000)]),NON(),LST([]))\
               .Crt(STR('*M1ATTRIBUTE'),U32(1),LST([STR('sells'),His(STR('o10')),I32(4)]),NON(),LST([]))\
               .Crt(STR('*M1COMPOSITION'),U32(1),LST([STR('products'),His(STR('o9')),His(STR('o10'))]),NON(),LST([]))\
               .Crt(STR('*M1OBJECT'),U32(1),LST([STR('warehouse__Product'),His(STR('o0')),STR('Lettuce')]),NON(),LST([]),resName='o11')\
               .Crt(STR('*M1ATTRIBUTE'),U32(1),LST([STR('name'),His(STR('o11')),STR('Lettuce')]),NON(),LST([]))\
               .Crt(STR('*M1ATTRIBUTE'),U32(1),LST([STR('price'),His(STR('o11')),F32(0.800000)]),NON(),LST([]))\
               .Crt(STR('*M1ATTRIBUTE'),U32(1),LST([STR('sells'),His(STR('o11')),I32(2)]),NON(),LST([]))\
               .Crt(STR('*M1COMPOSITION'),U32(1),LST([STR('products'),His(STR('o9')),His(STR('o11'))]),NON(),LST([]))\
               .Crt(STR('*M1COMPOSITION'),U32(1),LST([STR('categories'),His(STR('o3')),His(STR('o9'))]),NON(),LST([]))\
               .Crt(STR('*M1OBJECT'),U32(1),LST([STR('warehouse__Category'),His(STR('o0')),STR('milk')]),NON(),LST([]),resName='o12')\
               .Crt(STR('*M1ATTRIBUTE'),U32(1),LST([STR('name'),His(STR('o12')),STR('milk')]),NON(),LST([]))\
               .Crt(STR('*M1OBJECT'),U32(1),LST([STR('warehouse__Category'),His(STR('o0')),STR('cheese')]),NON(),LST([]),resName='o13')\
               .Crt(STR('*M1ATTRIBUTE'),U32(1),LST([STR('name'),His(STR('o13')),STR('cheese')]),NON(),LST([]))\
               .Crt(STR('*M1OBJECT'),U32(1),LST([STR('warehouse__Product'),His(STR('o0')),STR('Goat Cheese')]),NON(),LST([]),resName='o14')\
               .Crt(STR('*M1ATTRIBUTE'),U32(1),LST([STR('name'),His(STR('o14')),STR('Goat Cheese')]),NON(),LST([]))\
               .Crt(STR('*M1ATTRIBUTE'),U32(1),LST([STR('price'),His(STR('o14')),F32(5.000000)]),NON(),LST([]))\
               .Crt(STR('*M1ATTRIBUTE'),U32(1),LST([STR('sells'),His(STR('o14')),I32(0)]),NON(),LST([]))\
               .Crt(STR('*M1COMPOSITION'),U32(1),LST([STR('products'),His(STR('o13')),His(STR('o14'))]),NON(),LST([]))\
               .Crt(STR('*M1OBJECT'),U32(1),LST([STR('warehouse__Product'),His(STR('o0')),STR('Gouda')]),NON(),LST([]),resName='o15')\
               .Crt(STR('*M1ATTRIBUTE'),U32(1),LST([STR('name'),His(STR('o15')),STR('Gouda')]),NON(),LST([]))\
               .Crt(STR('*M1ATTRIBUTE'),U32(1),LST([STR('price'),His(STR('o15')),F32(2.000000)]),NON(),LST([]))\
               .Crt(STR('*M1ATTRIBUTE'),U32(1),LST([STR('sells'),His(STR('o15')),I32(100)]),NON(),LST([]))\
               .Crt(STR('*M1COMPOSITION'),U32(1),LST([STR('products'),His(STR('o13')),His(STR('o15'))]),NON(),LST([]))\
               .Crt(STR('*M1COMPOSITION'),U32(1),LST([STR('categories'),His(STR('o12')),His(STR('o13'))]),NON(),LST([]))\
               .Crt(STR('*M1OBJECT'),U32(1),LST([STR('warehouse__Product'),His(STR('o0')),STR('Cream')]),NON(),LST([]),resName='o16')\
               .Crt(STR('*M1ATTRIBUTE'),U32(1),LST([STR('name'),His(STR('o16')),STR('Cream')]),NON(),LST([]))\
               .Crt(STR('*M1ATTRIBUTE'),U32(1),LST([STR('price'),His(STR('o16')),F32(0.500000)]),NON(),LST([]))\
               .Crt(STR('*M1ATTRIBUTE'),U32(1),LST([STR('sells'),His(STR('o16')),I32(300)]),NON(),LST([]))\
               .Crt(STR('*M1COMPOSITION'),U32(1),LST([STR('products'),His(STR('o12')),His(STR('o16'))]),NON(),LST([]))\
               .Crt(STR('*M1OBJECT'),U32(1),LST([STR('warehouse__Product'),His(STR('o0')),STR('Milk')]),NON(),LST([]),resName='o17')\
               .Crt(STR('*M1ATTRIBUTE'),U32(1),LST([STR('name'),His(STR('o17')),STR('Milk')]),NON(),LST([]))\
               .Crt(STR('*M1ATTRIBUTE'),U32(1),LST([STR('price'),His(STR('o17')),F32(0.600000)]),NON(),LST([]))\
               .Crt(STR('*M1ATTRIBUTE'),U32(1),LST([STR('sells'),His(STR('o17')),I32(700)]),NON(),LST([]))\
               .Crt(STR('*M1COMPOSITION'),U32(1),LST([STR('products'),His(STR('o12')),His(STR('o17'))]),NON(),LST([]))\
               .Crt(STR('*M1COMPOSITION'),U32(1),LST([STR('categories'),His(STR('o3')),His(STR('o12'))]),NON(),LST([]))\
               .Crt(STR('*M1COMPOSITION'),U32(1),LST([STR('categories'),His(STR('o2')),His(STR('o3'))]),NON(),LST([]))\
               .Crt(STR('*M1OBJECT'),U32(1),LST([STR('warehouse__Category'),His(STR('o0')),STR('drinks')]),NON(),LST([]),resName='o18')\
               .Crt(STR('*M1ATTRIBUTE'),U32(1),LST([STR('name'),His(STR('o18')),STR('drinks')]),NON(),LST([]))\
               .Crt(STR('*M1OBJECT'),U32(1),LST([STR('warehouse__Category'),His(STR('o0')),STR('lemonade')]),NON(),LST([]),resName='o19')\
               .Crt(STR('*M1ATTRIBUTE'),U32(1),LST([STR('name'),His(STR('o19')),STR('lemonade')]),NON(),LST([]))\
               .Crt(STR('*M1OBJECT'),U32(1),LST([STR('warehouse__Product'),His(STR('o0')),STR('Coke')]),NON(),LST([]),resName='o20')\
               .Crt(STR('*M1ATTRIBUTE'),U32(1),LST([STR('name'),His(STR('o20')),STR('Coke')]),NON(),LST([]))\
               .Crt(STR('*M1ATTRIBUTE'),U32(1),LST([STR('price'),His(STR('o20')),F32(1.000000)]),NON(),LST([]))\
               .Crt(STR('*M1ATTRIBUTE'),U32(1),LST([STR('sells'),His(STR('o20')),I32(1000)]),NON(),LST([]))\
               .Crt(STR('*M1COMPOSITION'),U32(1),LST([STR('products'),His(STR('o19')),His(STR('o20'))]),NON(),LST([]))\
               .Crt(STR('*M1OBJECT'),U32(1),LST([STR('warehouse__Product'),His(STR('o0')),STR('Energy Drink')]),NON(),LST([]),resName='o21')\
               .Crt(STR('*M1ATTRIBUTE'),U32(1),LST([STR('name'),His(STR('o21')),STR('Energy Drink')]),NON(),LST([]))\
               .Crt(STR('*M1ATTRIBUTE'),U32(1),LST([STR('price'),His(STR('o21')),F32(10.000000)]),NON(),LST([]))\
               .Crt(STR('*M1ATTRIBUTE'),U32(1),LST([STR('sells'),His(STR('o21')),I32(0)]),NON(),LST([]))\
               .Crt(STR('*M1COMPOSITION'),U32(1),LST([STR('products'),His(STR('o19')),His(STR('o21'))]),NON(),LST([]))\
               .Crt(STR('*M1COMPOSITION'),U32(1),LST([STR('categories'),His(STR('o18')),His(STR('o19'))]),NON(),LST([]))\
               .Crt(STR('*M1OBJECT'),U32(1),LST([STR('warehouse__Product'),His(STR('o0')),STR('Coffee')]),NON(),LST([]),resName='o22')\
               .Crt(STR('*M1ATTRIBUTE'),U32(1),LST([STR('name'),His(STR('o22')),STR('Coffee')]),NON(),LST([]))\
               .Crt(STR('*M1ATTRIBUTE'),U32(1),LST([STR('price'),His(STR('o22')),F32(2.000000)]),NON(),LST([]))\
               .Crt(STR('*M1ATTRIBUTE'),U32(1),LST([STR('sells'),His(STR('o22')),I32(100)]),NON(),LST([]))\
               .Crt(STR('*M1COMPOSITION'),U32(1),LST([STR('products'),His(STR('o18')),His(STR('o22'))]),NON(),LST([]))\
               .Crt(STR('*M1OBJECT'),U32(1),LST([STR('warehouse__Product'),His(STR('o0')),STR('Hot Chocolate')]),NON(),LST([]),resName='o23')\
               .Crt(STR('*M1ATTRIBUTE'),U32(1),LST([STR('name'),His(STR('o23')),STR('Hot Chocolate')]),NON(),LST([]))\
               .Crt(STR('*M1ATTRIBUTE'),U32(1),LST([STR('price'),His(STR('o23')),F32(2.500000)]),NON(),LST([]))\
               .Crt(STR('*M1ATTRIBUTE'),U32(1),LST([STR('sells'),His(STR('o23')),I32(1)]),NON(),LST([]))\
               .Crt(STR('*M1COMPOSITION'),U32(1),LST([STR('products'),His(STR('o18')),His(STR('o23'))]),NON(),LST([]))\
               .Crt(STR('*M1COMPOSITION'),U32(1),LST([STR('categories'),His(STR('o2')),His(STR('o18'))]),NON(),LST([]))\
               .Crt(STR('*M1COMPOSITION'),U32(1),LST([STR('categories'),His(STR('o1')),His(STR('o2'))]),NON(),LST([]))
    #execute the command on the domain
    res = domain.Do(cmd,sessionId)
    m1model = res[0]
    return m1model