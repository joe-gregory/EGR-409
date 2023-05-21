from PySide.QtCore import*
from PySide.QtGui import*
import sys
from pint import UnitRegistry
import shaft_dialog
import time

ureg=UnitRegistry()


Pi=3.1415926535897

class MainDialog(QDialog,shaft_dialog.Ui_MainDialog):
    def __init__(self, parent=None):
        super(MainDialog,self).__init__(parent)
        self.setupUi(self)
        #All variables
        self.diameter=0.0
        self.E=0.0
        self.length=0.0
        self.factorsafety=1
        self.load1=[0,0]  #coordinate, load
        self.load2=[0,0]
        self.load3=[0,0]
        self.load4=[0,0]
        self.world_units='SI'  #SI or EN
        self.probset=0.0

        #Solution Variables
        self.moment_inertia=0.0
        self.torsion_moment=0.0
        self.load1_deflections=[0,0,0,0] #deflections caused by load 1 on coordinates 1,2,3, and 4 (which correspond to the coordinates by load 1,2,3, and 4, respectively)
        self.load2_deflections=[0,0,0,0]
        self.load3_deflections=[0,0,0,0]
        self.load4_deflections=[0,0,0,0]
        self.total_deflections=[0,0,0,0] #total deflections at coor xload1, xload2...
        self.ral=0.0
        self.dunk=0.0

        #connects and signals:
        self.comboBox_5.currentIndexChanged.connect(self.world_units_change)
        self.lineedit_shaft_diam.textChanged.connect(self.diameter_set)
        #self.lineedit_shaft_diam.textChanged.connect(setattr(diameter,ureg(self.lineedit_shaft_diam.tex())))
        self.lineEdit_elastic_mod.textChanged.connect(self.E_change)
        self.lineedit_shaft_length.textChanged.connect(self.shaft_length_change)
        self.spinbox_safety_factor.valueChanged.connect(self.safety_factor_change)
        self.lineedit_xcoo_load1.textChanged.connect(self.xcoo1)
        self.lineedit_xcoo_load2.textChanged.connect(self.xcoo2)
        self.lineedit_xcoo_load3.textChanged.connect(self.xcoo3)
        self.lineedit_xcoo_load4.textChanged.connect(self.xcoo4)
        self.lineedit_massweight_load1.textChanged.connect(self.mass1)
        self.lineedit_massweight_load2.textChanged.connect(self.mass2)
        self.lineedit_massweight_load3.textChanged.connect(self.mass3)
        self.lineedit_massweight_load4.textChanged.connect(self.mass4)
        self.calculate.clicked.connect(self.solve)

        #connects and signals for solutions side:
        self.comboBox.currentIndexChanged.connect(self.deflections_display)
        self.comboBox_2.currentIndexChanged.connect(self.deflections_display)
        self.comboBox_3.currentIndexChanged.connect(self.deflections_display)
        self.comboBox_4.currentIndexChanged.connect(self.deflections_display)

        #Methods for connects:
    def world_units_change(self):
        setattr(self,'world_units',self.comboBox_5.currentText())
        self.textBrowser.setPlainText('Unit System: '+ self.world_units)

        if(self.world_units=='SI'):
            self.lineedit_shaft_diam.setText(str(self.diameter.ito(ureg.mm))) #self.lineedit_shaft_diam.text()).ito(ureg.inch)
            self.diameter_set()

            self.lineEdit_elastic_mod.setText(str(self.E.ito(ureg.Mpascal)))
            self.E_change()

            self.lineedit_shaft_length.setText(str(self.length.ito(ureg.m)))
            self.shaft_length_change()

            self.lineedit_xcoo_load1.setText(str(self.load1[0].ito(ureg.m)))
            self.xcoo1()

        elif(self.world_units=='EN'):
            self.lineedit_shaft_diam.setText(str(self.diameter.ito(ureg.inch))) #self.lineedit_shaft_diam.text()).ito(ureg.inch)
            self.diameter_set()

            self.lineEdit_elastic_mod.setText(str(self.E.ito(ureg.klbf/(ureg.inch**2))))
            self.E_change()

            self.lineedit_shaft_length.setText(str(self.length.ito(ureg.inch)))
            self.shaft_length_change()

            self.lineedit_xcoo_load1.setText(str(self.load1[0].ito(ureg.inch)))
            self.xcoo1()
            #self.textBrowser.setPlainText('E changed to '+str(self.E))
            self.textBrowser.setPlainText('Diameter changed to '+str(self.diameter)+' E to '+str(self.E)+' length to '+str(self.length))


    def diameter_set(self):
        if(self.world_units=='SI'):
            try:
                setattr(self,'diameter',ureg(self.lineedit_shaft_diam.text()).ito(ureg.mm))
            except:
                self.textBrowser.setPlainText('diameter not defined correctly')

        elif(self.world_units=='EN'):
            try:
                setattr(self,'diameter',ureg(self.lineedit_shaft_diam.tex()).ito(ureg.inch))
            except:
                self.textBrowser.setPlainText('diameter not defined correctly')

        self.textBrowser.setPlainText('Diameter changed to '+str(self.diameter))
        self.probsetup()
        self.probsetup()


    def E_change(self):
        if(self.world_units=='SI'):
            try:
                setattr(self,'E',ureg(self.lineEdit_elastic_mod.text()).ito(ureg.Mpascal))
            except:
                self.textBrowser.setPlainText('Young modulus not defined correctly')
        elif(self.world_units=='EN'):
            try:
                setattr(self,'E',ureg(self.lineEdit_elastic_mod.text()).ito(ureg.klbf/(ureg.inch**2)))
            except:
                self.textBrowser.setPlainText('Young modulus not defined correctly')

        self.textBrowser.setPlainText('E changed to '+str(self.E))
        self.probsetup()

    def shaft_length_change(self):
        if(self.world_units=='SI'):
            try:
                setattr(self,'length',ureg(self.lineedit_shaft_length.text()).ito(ureg.meter))
            except:
                self.textBrowser.setPlainText('Shaft length not defined correctly')

        elif(self.world_units=='EN'):
            try:
                setattr(self,'length',ureg(self.lineedit_shaft_length.text()).ito(ureg.inch))
            except:
                self.textBrowser.setPlainText('Shaft length not defined correctly')

        self.textBrowser.setPlainText('Length changed to '+str(self.length))
        self.probsetup()

    def safety_factor_change(self):
        setattr(self,'factorsafety',int(self.spinbox_safety_factor.value()))
        self.textBrowser.setPlainText("Factor of safety has been set to "+ str(self.factorsafety))
        self.probsetup()

    def xcoo1(self):
        if(self.world_units=='SI'):
            try:
                self.load1[0]=ureg(self.lineedit_xcoo_load1.text()).ito(ureg.meter)
            except:
                self.textBrowser.setPlainText('Coordinate 1 not defined correctly')

        elif (self.world_units=='EN'):
            try:
                self.load1[0]=ureg(self.lineedit_xcoo_load1.text()).ito(ureg.inch)
            except:
                self.textBrowser.setPlainText('Coordinate 1 not defined correctly')

        self.textBrowser.setPlainText("Coordinate 1 changed to: "+ str(self.load1[0]))
        self.probsetup()

    def xcoo2(self):
        if(self.world_units=='SI'):
            try:
                self.load2[0]=ureg(self.lineedit_xcoo_load2.text()).ito(ureg.meter)
            except:
                self.textBrowser.setPlainText('Coordinate 2 not defined correctly')

        elif (self.world_units=='EN'):
            try:
                self.load2[0]=ureg(self.lineedit_xcoo_load2.text()).ito(ureg.inch)
            except:
                self.textBrowser.setPlainText('Coordinate 2 not defined correctly')

        self.textBrowser.setPlainText("Coordinate 2 changed to: "+ str(self.load2[0]))
        self.probsetup()

    def xcoo3(self):
        if(self.world_units=='SI'):
            try:
                self.load3[0]=ureg(self.lineedit_xcoo_load3.text()).ito(ureg.meter)
            except:
                self.textBrowser.setPlainText('Coordinate 3 not defined correctly')

        elif (self.world_units=='EN'):
            try:
                self.load3[0]=ureg(self.lineedit_xcoo_load3.text()).ito(ureg.inch)
            except:
                self.textBrowser.setPlainText('Coordinate 3 not defined correctly')

        self.textBrowser.setPlainText("Coordinate 3 changed to: "+ str(self.load3[0]))
        self.probsetup()

    def xcoo4(self):
        if(self.world_units=='SI'):
            try:
                self.load4[0]=ureg(self.lineedit_xcoo_load4.text()).ito(ureg.meter)
            except:
                self.textBrowser.setPlainText('Coordinate 4 not defined correctly')

        elif (self.world_units=='EN'):
            try:
                self.load4[0]=ureg(self.lineedit_xcoo_load4.text()).ito(ureg.inch)
            except:
                self.textBrowser.setPlainText('Coordinate 4 not defined correctly')

        self.textBrowser.setPlainText("Coordinate 4 changed to: "+ str(self.load4[0]))
        self.probsetup()

    def mass1(self):
        if(self.world_units=='SI'):
            try:
                self.load1[1]=ureg(self.lineedit_massweight_load1.text()).ito(ureg.kg)
            except:
                self.textBrowser.setPlainText('Masses need to be entered in mass units like g, kg, etc.')
        #maybe switch this two to be able to accept force units
        elif(self.world_units=='EN'):
            try:
                self.load1[1]=ureg(self.lineedit_massweight_load1.text()).ito(ureg.lb)
            except:
                self.textBrowser.setPlainText('Masses need to be entered in mass units. Note that lb stands for lb mass while lbf stands for lb force.')
        self.textBrowser.setPlainText("Mass 1 set to: "+ str(self.load1[1]))
        self.probsetup()

    def mass2(self):
        if(self.world_units=='SI'):
            try:
                self.load2[1]=ureg(self.lineedit_massweight_load2.text()).ito(ureg.kg)
            except:
                self.textBrowser.setPlainText('Masses need to be entered in mass units like g, kg, etc.')

        elif(self.world_units=='EN'):
            try:
                self.load2[1]=ureg(self.lineedit_massweight_load2.text()).ito(ureg.lb)
            except:
                self.textBrowser.setPlainText('Masses need to be entered in mass units. Note that lb stands for lb mass while lbf stands for lb force.')
        self.textBrowser.setPlainText("Mass 2 set to: "+ str(self.load2[1]))
        self.probsetup()

    def mass3(self):
        if(self.world_units=='SI'):
            try:
                self.load3[1]=ureg(self.lineedit_massweight_load3.text()).ito(ureg.kg)
            except:
                self.textBrowser.setPlainText('Masses need to be entered in mass units like g, kg, etc.')

        elif(self.world_units=='EN'):
            try:
                self.load3[1]=ureg(self.lineedit_massweight_load3.text()).ito(ureg.lb)
            except:
                self.textBrowser.setPlainText('Masses need to be entered in mass units. Note that lb stands for lb mass while lbf stands for lb force.')
        self.textBrowser.setPlainText("Mass 3 set to: "+ str(self.load3[1]))
        self.probsetup()

    def mass4(self):
        if(self.world_units=='SI'):
            try:
                self.load4[1]=ureg(self.lineedit_massweight_load4.text()).ito(ureg.kg)
            except:
                self.textBrowser.setPlainText('Masses need to be entered in mass units like g, kg, etc.')

        elif(self.world_units=='EN'):
            try:
                self.load4[1]=ureg(self.lineedit_massweight_load4.text()).ito(ureg.lb)
            except:
                self.textBrowser.setPlainText('Masses need to be entered in mass units. Note that lb stands for lb mass while lbf stands for lb force.')
        self.textBrowser.setPlainText("Mass 4 set to: "+ str(self.load4[1]))
        self.probsetup()

    def probsetup(self):
        x=0
        if(self.diameter != 0.0):
            x+=16
        if(self.E != 0.0):
            x+=16
        if(self.length != 0.0):
            x+=16
        if(self.factorsafety != 0.0):
            x+=16
        if(((self.load1[0] and self.load1[1]) or (self.load2[0] and self.load2[1]) or (self.load3[0] and self.load3[1]) or (self.load4[0] and self.load4[1])) != 0):
            x+=36
        self.progressBar.setValue(x)

        #Solver functions
    def solve(self):
        self.moment_inert()
        self.tors_moment()
        self.deflections()

        #Bending natural frequencies
        self.nat_freqs()

        self.results_display()

    #This is the method for displaying results
    def results_display(self):
        #Inertias:
        self.lineedit_bendinginertia.setText(str(self.moment_inertia))
        self.lineedit_torsioninertia.setText(str(self.torsion_moment))

        #Manual deflections display of totals: self.total_deflections=[0,0,0,0]
        self.lineedit_point1_deflection.setText(str(self.total_deflections[0]))
        self.lineedit_point2_deflection.setText(str(self.total_deflections[1]))
        self.lineedit_point3_deflection.setText(str(self.total_deflections[2]))
        self.lineedit_shaft_diam_5.setText(str(self.total_deflections[3]))

        #Raleighs and Dunkerleys display:
        self.lineedit_natfreq_ral.setText(str(self.ral))
        self.lineedit_natfreq_dunk.setText(str(self.dunk))

    def deflections_display(self):

        if(self.comboBox.currentText()=='Total'):
            self.lineedit_point1_deflection.setText(str(self.total_deflections[0]))
        elif(self.comboBox.currentText()=='Load 1'):
            self.lineedit_point1_deflection.setText(str(self.load1_deflections[0]))
        elif(self.comboBox.currentText()=='Load 2'):
            self.lineedit_point1_deflection.setText(str(self.load2_deflections[0]))
        elif(self.comboBox.currentText()=='Load 3'):
            self.lineedit_point1_deflection.setText(str(self.load3_deflections[0]))
        elif(self.comboBox.currentText()=='Load 4'):
            self.lineedit_point1_deflection.setText(str(self.load4_deflections[0]))
        else:
            self.textBrowser.setPlainText('No condition reached in num1 deflection_display')


        if(self.comboBox_2.currentText()=='Total'):
            self.lineedit_point2_deflection.setText(str(self.total_deflections[1]))
        elif(self.comboBox_2.currentText()=='Load 1'):
            self.lineedit_point2_deflection.setText(str(self.load1_deflections[1]))
        elif(self.comboBox_2.currentText()=='Load 2'):
            self.lineedit_point2_deflection.setText(str(self.load2_deflections[1]))
        elif(self.comboBox_2.currentText()=='Load 3'):
            self.lineedit_point2_deflection.setText(str(self.load3_deflections[1]))
        elif(self.comboBox_2.currentText()=='Load 4'):
            self.lineedit_point2_deflection.setText(str(self.load4_deflections[1]))
        else:
            self.textBrowser.setPlainText('No condition reached in num2 deflection_display')


        if(self.comboBox_3.currentText()=='Total'):
            self.lineedit_point3_deflection.setText(str(self.total_deflections[2]))
        elif(self.comboBox_3.currentText()=='Load 1'):
            self.lineedit_point3_deflection.setText(str(self.load1_deflections[2]))
        elif(self.comboBox_3.currentText()=='Load 2'):
            self.lineedit_point3_deflection.setText(str(self.load2_deflections[2]))
        elif(self.comboBox_3.currentText()=='Load 3'):
            self.lineedit_point3_deflection.setText(str(self.load3_deflections[2]))
        elif(self.comboBox_3.currentText()=='Load 4'):
            self.lineedit_point3_deflection.setText(str(self.load4_deflections[2]))
        else:
            self.textBrowser.setPlainText('No condition reached in num3 deflection_display')


        if(self.comboBox_4.currentText()=='Total'):
            self.lineedit_shaft_diam_5.setText(str(self.total_deflections[3]))
        elif(self.comboBox_4.currentText()=='Load 1'):
            self.lineedit_shaft_diam_5.setText(str(self.load1_deflections[3]))
        elif(self.comboBox_4.currentText()=='Load 2'):
            self.lineedit_shaft_diam_5.setText(str(self.load2_deflections[3]))
        elif(self.comboBox_4.currentText()=='Load 3'):
            self.lineedit_shaft_diam_5.setText(str(self.load3_deflections[3]))
        elif(self.comboBox_4.currentText()=='Load 4'):
            self.lineedit_shaft_diam_5.setText(str(self.load4_deflections[3]))
        else:
            self.textBrowser.setPlainText('No condition reached in num4 deflection_display')

    #Solution variable functions
    def moment_inert(self):
        self.moment_inertia=Pi*(self.diameter**4)/64.0

    def tors_moment(self):
        self.torsion_moment=Pi*(self.diameter**4)/32.0

    def deflector_mod(self,load,X): #inputs: Mass, X coordinated at which deflection is wanted
        if(self.world_units=='SI'): #Note this function can be used for any X coor in the shaft
            F=load[1]*9.8*ureg['meter/second**2']
        elif(self.world_units=='EN'):
            F=load[1]*32.174*ureg['foot/second**2']
        else:
             self.textBrowser.setPlainText("Units Error in deflector the Monster function")

        if(load[0]<=self.length/2):
            b=self.length-load[0]
            a=load[0]
            x=X
        elif(load[0]>self.length/2):
            b=load[0]
            a=self.length-load[0]
            x=self.length-X
        elif(load[0]==(self.length/2)):
            #Equation for right in the middle
            x=X
            y=F*x*(4*x**2-3*self.length**2)/(48*self.E*self.moment_inertia)
        else:
            self.textBrowser.setPlainText("Unable to identify deflection variables in deflector mod")
            #Reminder: self.load1=[0,0]  #coordinate, load
        #self.textBrowser.setPlainText('a:'+str(type(a))+'x:'+str(type(x))+'x.mag:'+str(type(x.magnitude)))
        #Calculating deflection caused at x by load[1]
        try:
            x.magnitude
            pass
        except AttributeError:
            return(0*ureg['mm'])

        try:
            a.magnitude
            pass
        except AttributeError:
            return(0*ureg['mm'])

        if((x.magnitude)<=(a.magnitude)):
            try:
                y=F*b*x*(x**2+b**2-self.length**2)/(6*self.E*self.moment_inertia*self.length)
            except:
                y=0*ureg['mm'] #maybe this?
        elif((x.magnitude)>(a.magnitude)):
            try:
                y=F*a*(self.length-x)*(x**2+a**2-2*self.length*x)/(6*self.E*self.moment_inertia*self.length)
            except:
                y=0*ureg['mm']
        else:
            self.textBrowser.setPlainText("Deflection calculation error in deflector mod")
        y.ito(ureg.mm)
        return(-y)
    #Deflections
    def deflections(self):
        #The deflections caused by Load 1 on Coor 1,2,3,4
        #self.load1_deflections=[0,0,0,0]
        if(self.load1[1]!=0):
            self.load1_deflections[0]=self.deflector_mod(self.load1,self.load1[0])
            self.load1_deflections[1]=self.deflector_mod(self.load1,self.load2[0])
            self.load1_deflections[2]=self.deflector_mod(self.load1,self.load3[0])
            self.load1_deflections[3]=self.deflector_mod(self.load1,self.load4[0])


        if(self.load2[1]!=0):
            self.load2_deflections[0]=self.deflector_mod(self.load2,self.load1[0])
            self.load2_deflections[1]=self.deflector_mod(self.load2,self.load2[0])
            self.load2_deflections[2]=self.deflector_mod(self.load2,self.load3[0])
            self.load2_deflections[3]=self.deflector_mod(self.load2,self.load4[0])


        if(self.load3[1]!=0):
            self.load3_deflections[0]=self.deflector_mod(self.load3,self.load1[0])
            self.load3_deflections[1]=self.deflector_mod(self.load3,self.load2[0])
            self.load3_deflections[2]=self.deflector_mod(self.load3,self.load3[0])
            self.load3_deflections[3]=self.deflector_mod(self.load3,self.load4[0])


        if(self.load4[1]!=0):
            self.load4_deflections[0]=self.deflector_mod(self.load4,self.load1[0])
            self.load4_deflections[1]=self.deflector_mod(self.load4,self.load2[0])
            self.load4_deflections[2]=self.deflector_mod(self.load4,self.load3[0])
            self.load4_deflections[3]=self.deflector_mod(self.load4,self.load4[0])


        if(self.load1[1]!=0):
            self.total_deflections[0]=self.load1_deflections[0]+self.load2_deflections[0]+self.load3_deflections[0]+self.load4_deflections[0]
        if(self.load2[1]!=0):
            self.total_deflections[1]=self.load1_deflections[1]+self.load2_deflections[1]+self.load3_deflections[1]+self.load4_deflections[1]
        if(self.load3[1]!=0):
            self.total_deflections[2]=self.load1_deflections[2]+self.load2_deflections[2]+self.load3_deflections[2]+self.load4_deflections[2]
        if(self.load4[1]!=0):
            self.total_deflections[3]=self.load1_deflections[3]+self.load2_deflections[3]+self.load3_deflections[3]+self.load4_deflections[3]

        #Up to this point I should have the deflections at the coordinates of the loads by all the loads
        #The methods for deflection display will be separate
        #Reminder: self.load1=[0,0]  #coordinate, load
    #self.load1_deflections=[0,0,0,0] #deflections caused by load 1 on coordinates 1,2,3, and 4 (which correspond to the coordinates by load 1,2,3, and 4, respectively)
    #self.total_deflections=[0,0,0,0] #total deflections at coor xload1, xload2...
    #deflector mod is used by deflections to calculate deflections at given coor and load

    def nat_freqs(self):
        if(self.world_units=='SI'):
            g=9.8*ureg['meter/second**2']
        elif(self.world_units=='EN'):
            g=32.174*ureg['foot/second**2']
        else:
            self.textBrowser.setPlainText("Error in Ral Method")
        #Reminder: self.load1=[0,0]  #coordinate, load

        ral=g*(self.load1[1]*self.total_deflections[0]+self.load2[1]*self.total_deflections[1]+self.load3[1]*self.total_deflections[2]+self.load4[1]*self.total_deflections[3])/(self.load1[1]*self.total_deflections[0]**2+self.load2[1]*self.total_deflections[1]**2+self.load3[1]*self.total_deflections[2]**2+self.load4[1]*self.total_deflections[3]**2)
        ral=ral**0.5
        self.ral=ral.ito(ureg.rad/ureg.second)

        #Dunkerleys
        try:
            w11=(g/self.load1_deflections[0])**0.5
        except:
            w11=0
        try:
            w22=(g/self.load2_deflections[1])**0.5
        except:
            w22=0
        try:
            w33=(g/self.load3_deflections[2])**0.5
        except:
            w33=0
        try:
            w44=(g/self.load4_deflections[3])**0.5
        except:
            w44=0

        critical_speeds=[w11,w22,w33,w44]
        n=0
        cs_sum=0
        while(critical_speeds[n]!=0):
            cs_sum+=1/critical_speeds[n]**2
            n+=1

        dunk=(1/cs_sum)**0.5
        self.dunk=dunk.ito(ureg.rad/ureg.second)


app=QApplication(sys.argv)
form=MainDialog()
form.show()
app.exec_()