import sys,io,numpy
from PyQt5.QtCore import Qt,QPoint
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QRadioButton, QLabel, QSizePolicy,QFileDialog
from PyQt5.QtGui import QColor, QPainter, QPixmap, QPen,QPolygon
import inspect
import time
#2_2_6再次加强了显示的效果把漏掉的点填上
class OpenGLView(QWidget):
    def __init__(self, parent=None):
        super(OpenGLView, self).__init__()
        #参数变量
        self.colorBuffer=[[QColor(255,255,255) for i in range(700)] for j in range(700) ]#深度缓存
        self.zBuffer=[[-1000000.0 for i in range(0,700)] for j in range(700)]#颜色缓存
        self.filePath = r"./tmp.txt"#自定义文件的路径
        #self.filePath=r"C:/Users/user/Desktop/currentWork/zbufferTest1.txt"
        #self.filePath = r"C:\Users\user\Desktop\homework\CG\r1_1.txt"
        self.ObjfilePath =r"C:\Users\user\Desktop\homework\CG\rabbit1.obj"#OBJ文件的路径
        self.setFixedSize(900, 900)  # 设置窗口大小
        self.setWindowTitle('消隐算法的实现')
        # 控件声明
        self.pix = QPixmap(700, 700)
        self.pix.fill(Qt.white)
        self.draw_btn = QPushButton("绘制", self)
        self.file_btn = QPushButton("选择自定义文件", self)
        self.fileObj_btn = QPushButton("选择Obj文件", self)
        self.Obj_btn = QPushButton("加载Obj文件", self)
        self.exit_btn = QPushButton("清空", self)
        self.radio_buttonMethod1 = QRadioButton('zbuffer算法')
        self.radio_buttonMethod2 = QRadioButton('光线投射算法')
        self.radio_buttonMethod3 = QRadioButton('无算法')
        self.radio_buttonMethod1.setChecked(True)
        # 标签
        self.pixLabel = QLabel()
        self.pixLabel.setAlignment(Qt.AlignCenter)  # 将 QLabel 居中显示
        self.pixLabel.setScaledContents(True)  # 启用自动缩放
        self.pixLabel.setPixmap(self.pix)
        self.openGLLabel = QLabel(self)
        self.openGLLabel.setText('画图界面')
        self.openGLLabel.setStyleSheet("QLabel {color: #00BFFF; font-weight: bold;font-size: 20px;}")
        self.GLinteractLabel = QLabel(self)
        self.GLinteractLabel.setText('菜单')
        self.GLinteractLabel.setStyleSheet("QLabel {color: #00BFFF; font-weight: bold;font-size: 20px;}")
        self.timeLabel = QLabel()
        self.timeLabel.setStyleSheet("QLabel {color: #FF0000; font-weight: bold;font-size: 20px;}")
        # 创建布局
        vBox = QVBoxLayout(self)
        openGLBox = QHBoxLayout(self)
        GLinteractBox = QHBoxLayout(self)
        labelBox1 = QHBoxLayout(self)
        labelBox2 = QHBoxLayout(self)
        selectBox = QHBoxLayout(self)
        # 布局添加控件
        openGLBox.addWidget(self.pixLabel)
        GLinteractBox.addWidget(self.draw_btn)
        GLinteractBox.addWidget(self.exit_btn)
        GLinteractBox.addWidget(self.file_btn)
        GLinteractBox.addWidget(self.fileObj_btn)
        labelBox1.addWidget(self.openGLLabel)
        labelBox2.addWidget(self.GLinteractLabel)
        selectBox.addWidget(self.radio_buttonMethod1)
        selectBox.addWidget(self.radio_buttonMethod2)
        selectBox.addWidget(self.radio_buttonMethod3)
        selectBox.addWidget(self.Obj_btn)
        # 控件功能的连接
        #self.exit_btn.clicked.connect(self.close)
        self.exit_btn.clicked.connect(self.clear)
        self.Obj_btn.clicked.connect(self.ReadObject)
        self.draw_btn.clicked.connect(self.buttonClicked)
        self.file_btn.clicked.connect(self.showFileDialog)
        self.fileObj_btn.clicked.connect(self.showFileDialog)
        # 布局的嵌套
        vBox.addLayout(labelBox1)
        vBox.addLayout(openGLBox)
        vBox.addWidget(self.timeLabel)
        vBox.addLayout(labelBox2)
        vBox.addLayout(selectBox)
        vBox.addLayout(GLinteractBox)
    def buttonClicked(self):
        self.draw()
    def clear(self):
        self.pix.fill(Qt.white)
        self.pixLabel.setPixmap(self.pix)
    def initBuffer(self):
        self.timeLabel.setText("正在加载。。。。。。")
        self.timeLabel.repaint()
        for i in range(700):
            for j in range(700):
                self.zBuffer[i][j]=-1000000
                self.colorBuffer[i][j]=QColor(255,255,255)
        #self.pix.fill(Qt.white)
    def showFileDialog(self):#选择文件
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.AnyFile)  # 设置文件选择模式为任意文件
        file_dialog.exec_()  # 打开文件对话框
        selected_files = file_dialog.selectedFiles()  # 获取用户选择的文件
        sender=self.sender()
        if selected_files:
            if sender.text()=="选择Obj文件":
                self.ObjfilePath = selected_files[0]
                self.ReadObject()
            else:
                self.filePath = selected_files[0]
    def ReadObject(self):#把OBJ转成自定义的格式
        file = io.StringIO()
        time1 = time.time()
        listX = []
        listY = []
        listZ = []
        listVNX = []
        listVNY = []
        listVNZ = []
        listF = []
        listFN = []  # 法向量
        lightDir = numpy.array([0, 0, -1])
        # ambient = numpy.array([0.2, 0.2, 0.2])
        ambient = 80  # 环境光强
        # specular=numpy.array([0.8,0.8,0.8])
        specular = 80  # 镜面反射光强
        # diffuse=numpy.array([0,0,0])
        diffuse = 160  # 漫反射光强
        with open(self.ObjfilePath) as f:
            line = f.readline()
            while line != "":
                linelist = line.split()
                if len(linelist) > 0 and linelist[0] == "v":
                    listX.append(float(linelist[1]))
                    listY.append(float(linelist[2]))
                    listZ.append(float(linelist[3]))
                if len(linelist) > 0 and linelist[0] == "f":#加载索引
                    fline = []  # 一个面片列表
                    fNline = []
                    for i in range(1, 4):
                        nlist = linelist[i].split("//")
                        fline.append(int(nlist[0]))
                        fNline.append(int(nlist[1]))  # 顶点的法向量
                    listF.append(fline)
                    listFN.append(fNline)
                if len(linelist) > 0 and linelist[0] == "vn":#加载法向量
                    listVNX.append(float(linelist[1]))
                    listVNY.append(float(linelist[2]))
                    listVNZ.append(float(linelist[3]))
                line = f.readline()
        maxX = max(listX)
        minX = min(listX)
        maxY = max(listY)
        minY = min(listY)
        minNum = min(minX, minY)
        # 把最小的数都变成1
        listX = [((x + 1 - minX)) for x in listX]
        listY = [((y + 1 - minY)) for y in listY]
        maxX = max(listX)
        minX = min(listX)
        maxY = max(listY)
        minY = min(listY)
        print("最小的为1后")
        print("maxX=", max(listX), ",minX=", min(listX))
        print("maxY=", max(listY), ",minY=", min(listY))
        maxRange=max(maxX,maxY)
        Multiplier = (600 / maxRange)  # 求缩放比例
        #print("Xoffset",Xoffset)
        #print("Yoffset", Yoffset)
        listX = [(x * Multiplier) for x in listX]
        listY = [(y* Multiplier) for y in listY]
        #listZ = [int((z) * Multiplier) for z in listZ]
        listZ = [z*Multiplier for z in listZ]

        print("maxX=", max(listX))
        print("maxY=", max(listY))

        Xoffset =345-(max(listX)+min(listX))/ 2#将模型中间的点画到模型中间即可
        Yoffset =345-(max(listY)+min(listY))/ 2
        listX = [(x+Xoffset) for x in listX]
        listY = [(y+Yoffset) for y in listY]

        print("maxX=",max(listX))
        print("maxY=", max(listY))


        # 法向量平均即可
        for i in range(0, len(listF)):
            listVector = []
            for j in range(0, 3):
                # print(listF[i][j]-1)
                file.write(str(listX[listF[i][j] - 1]) + ' ')
                file.write(str(listY[listF[i][j] - 1]) + ' ')
                file.write(str(listZ[listF[i][j] - 1]) + ' ')

                listVector.append(
                    numpy.array([listVNX[listFN[i][j] - 1], listVNY[listFN[i][j] - 1], listVNZ[listFN[i][j] - 1]]))
            V = (listVector[0] + listVector[1] + listVector[2])
            if numpy.linalg.norm(V) == 0:
                file.write(str(ambient) + ' ' + str(ambient) + " " + str(ambient) + '\n')
            else:
                normalV = V / numpy.linalg.norm(V)
                K = max(normalV[2] * (-1), 0)  # 漫反射的强度N*L
                #R =numpy.array([0,0,-1])-2*normalV[2]*(-1)*normalV#反射向量
                rgbstr = str((diffuse * K + ambient + specular * (1*(-1-2*normalV[2]*(-1)*normalV[2]))))
                # file.write('192 192 192\n')
                file.write(rgbstr + " " + rgbstr + " " + rgbstr + '\n')
        print("maxX=", max(listX), ",minX=", min(listX))
        print("maxY=", max(listY), ",minY=", min(listY))
        print("maxZ=", max(listZ), ",minZ=", min(listZ))
        print("用时", time.time() - time1, "秒")
        # 把面的顶点加载
        file.seek(0)
        line = file.readline()
        while line != "":
            #print(line)
            line = file.readline()
        #output_file = r"C:\Users\user\Desktop\homework\CG\rabbit2_0.txt"
        output_file = r"./tmpMyForm.txt"
        self.filePath=output_file
        with open(output_file, 'w') as f:
            f.write(file.getvalue())
        file.close()
        
    def draw(self):
        print("当前函数名为", inspect.currentframe().f_code.co_name)
        if self.radio_buttonMethod1.isChecked():
            self.ReadAndDrawZbuffer()
        elif self.radio_buttonMethod2.isChecked():
            self.ReadAndDrawRayCasting()
        elif self.radio_buttonMethod3.isChecked():
            self.ReadAndDraw()
    def ReadAndDraw(self):
        self.clear()
        start_time = time.time()
        with open(self.filePath, 'r') as f:
            line = f.readline()
            while line != '':
                Glist = line.split()
                if len(Glist) == 12:
                    self.drawTriangle0(float(Glist[0]), float(Glist[1]), float(Glist[2]), float(Glist[3]), float(Glist[4]),
                                      float(Glist[5]), float(Glist[6]), float(Glist[7]), float(Glist[8]), float(Glist[9]),
                                      float(Glist[10]), float(Glist[11]))
                elif len(Glist) == 15:
                    self.drawRect0(float(Glist[0]), float(Glist[1]), float(Glist[2]), float(Glist[3]), float(Glist[4]),
                                  float(Glist[5]), float(Glist[6]), float(Glist[7]), float(Glist[8]), float(Glist[9]),
                                  float(Glist[10]), float(Glist[11]), float(Glist[12]), float(Glist[13]), float(Glist[14]))
                line = f.readline()
        end_time = time.time()
        print("绘画用时{}秒".format(end_time - start_time))
        self.timeLabel.setText("无算法:绘画用时{}秒".format(end_time - start_time))
    def ReadAndDrawZbuffer(self):
        self.clear()
        self.initBuffer()
        start_time=time.time()
        with open(self.filePath,'r') as f:
            line=f.readline()
            while line!='':
                Glist=line.split()
                if len(Glist)==12:
                    self.drawTriangle(float(Glist[0]),float(Glist[1]),float(Glist[2]),float(Glist[3]),float(Glist[4]),float(Glist[5]),float(Glist[6]),float(Glist[7]),float(Glist[8]),float(Glist[9]),float(Glist[10]),float(Glist[11]))
                elif len(Glist) == 15:
                    self.drawRect(float(Glist[0]),float(Glist[1]),float(Glist[2]),float(Glist[3]),float(Glist[4]),float(Glist[5]),float(Glist[6]),float(Glist[7]),float(Glist[8]),float(Glist[9]),float(Glist[10]),float(Glist[11]),float(Glist[12]),float(Glist[13]),float(Glist[14]))
                line=f.readline()
                pass
        end_time = time.time()
        print("绘画用时{}秒".format(end_time-start_time))
        self.timeLabel.setText("Zbuffer:绘画用时{}秒".format(end_time-start_time))
    def initRayCasting(self):#初始化光线投射算法
        self.timeLabel.setText("正在加载。。。。。。")
        self.timeLabel.repaint()
    def ReadAndDrawRayCasting(self):#光线投射算法
        self.clear()
        self.initRayCasting()
        start_time = time.time()
        painter = QPainter(self.pix)
        GraphicsList3v = []#三角形
        Equation3v=[]#面的方程
        GraphicsList4v = []#四边形
        Equation4v = []  # 面的方程
        with open(self.filePath, 'r') as f:#加载完全部图形,并计算出面的方程
            line=f.readline()
            while line!='':
                GList=line.split()
                if len(GList) == 12:
                    GraphicsList3v.append([float(elem) for elem in GList])
                    x1, y1, z1, x2, y2, z2, x3, y3, z3, c1, c2, c3=GraphicsList3v[-1]
                    Equation3v.append(self.getEquation(x1, y1, z1, x2, y2, z2, x3, y3, z3))
                elif len(GList) == 15:
                    GraphicsList4v.append([float(elem) for elem in GList])
                    x1, y1, z1, x2, y2, z2, x3, y3, z3, x4, y4, z4, c1, c2, c3=GraphicsList4v[-1]
                    Equation4v.append(self.getEquation(x1, y1, z1, x2, y2, z2, x3, y3, z3))
                line = f.readline()
        for y in range(700):#光线投射
            print("y=",y)
            for x in range(700):#为什么xy不能换？#光线投射算法判断点的颜色
                zmax=-1000000
                color=QColor(255,255,255)
                for i in range(0,len(GraphicsList3v)):
                    #射线法判断是否在图形的内部,引一条水平射线01 34 67 x=(x1-x2)/(y1-y2)*(y-y1)+x1
                    listp=[]
                    x1, y1, z1, x2, y2, z2, x3, y3, z3, c1, c2, c3=GraphicsList3v[i]
                    if (x==x1 and y==y1) or (x==x2 and y==y2) or (x==x3 and y==y3):#处理端点
                        ztemp = (-Equation3v[i][0] * x - Equation3v[i][1] * y - Equation3v[i][3]) / Equation3v[i][2]
                        if ztemp >= zmax:
                            zmax = ztemp
                            color = QColor(c1, c2, c3)
                    #处理水平的最高最低线
                    if (y==y1 and y1==y2 and ((x<=x1 and x>=x2) or (x>=x1 and x<=x2))):
                        ztemp = (-Equation3v[i][0] * x - Equation3v[i][1] * y - Equation3v[i][3]) / Equation3v[i][2]
                        if ztemp >= zmax:
                            zmax = ztemp
                            color = QColor(c1, c2, c3)
                    elif (y==y2 and y2==y3 and ((x<=x2 and x>=x3) or (x>=x2 and x<=x3))):
                        ztemp = (-Equation3v[i][0] * x - Equation3v[i][1] * y - Equation3v[i][3]) / Equation3v[i][2]
                        if ztemp >= zmax:
                            zmax = ztemp
                            color = QColor(c1, c2, c3)
                    elif (y==y3 and y1==y3 and ((x<=x1 and x>=x3) or (x>=x1 and x<=x3))):
                        ztemp = (-Equation3v[i][0] * x - Equation3v[i][1] * y - Equation3v[i][3]) / Equation3v[i][2]
                        if ztemp >= zmax:
                            zmax = ztemp
                            color = QColor(c1, c2, c3)
                    if (y>=y1 and y>=y2 and y>=y3) or (y<=y1 and y<=y2 and y<=y3): #or(y1==y2 and y2==y3):#下一个图形
                        continue
                    if (x>=x1 and x>=x2 and x>=x3) or (x<=x1 and x<=x2 and x<=x3): #or (x1==x2 and x2==x3):#下一个图形
                        continue
                    #ztemp = (-Equation3v[i][0] * x - Equation3v[i][1] * y - Equation3v[i][3]) / Equation3v[i][2]
                    #if ztemp < zmax:
                    #   continue
                    if y1!=y2:
                        x0=(x1-x2)/(y1-y2)*(y-y1)+x1
                        if x>=x0 and ((x0<=x1 and x0>=x2)or (x0>=x1 and x0<=x2)) and ((y<=y1 and y>=y2)or (y>=y1 and y<=y2)):
                            listp.append(x0)
                    if y2!=y3:
                        x0=(x2-x3)/(y2-y3)*(y-y2)+x2
                        if x>=x0 and ((x0<=x2 and x0>=x3)or (x0>=x2 and x0<=x3)) and ((y<=y2 and y>=y3)or (y>=y2 and y<=y3)):
                            listp.append(x0)
                    if y1!=y3:
                        x0=(x1-x3)/(y1-y3)*(y-y3)+x3
                        if x>=x0 and ((x0<=x1 and x0>=x3)or (x0>=x1 and x0<=x3)) and ((y<=y1 and y>=y3)or (y>=y1 and y<=y3)):
                            listp.append(x0)
                    if len(listp)==3 or len(listp)==0:
                        continue
                    elif len(listp)==2 and (abs(listp[1]-listp[0])>0.0001):
                        continue
                    if Equation3v[i][2]==0:
                        continue
                    ztemp=(-Equation3v[i][0]*x-Equation3v[i][1]*y-Equation3v[i][3])/Equation3v[i][2]
                    if ztemp>=zmax:
                        zmax=ztemp
                        color=QColor(c1,c2,c3)
                for i in range(0, len(GraphicsList4v)):
                    # 射线法判断是否在图形的内部,引一条水平射线交点的横坐标是x=(x1-x2)/(y1-y2)*(y-y1)+x1,如果x0在线段上。。。
                    pNum = 0
                    x1, y1, z1, x2, y2, z2, x3, y3, z3, x4, y4, z4, c1, c2, c3 = GraphicsList4v[i]
                    if (y > y1 and y > y2 and y > y3 and y > y4) or (y < y1 and y < y2 and y < y3 and y < y4):  # 下一个图形
                        continue
                    if (x > x1 and x > x2 and x > x3 and x > x4) or (x < x1 and x < x2 and x < x3 and x < x4) or Equation4v[i][2]==0:  # 下一个图形
                        continue
                    if y1 != y2:
                        x0 = (x1 - x2) / (y1 - y2) * (y - y1) + x1#(x0,y),(x,y)
                        if x >= x0 and ((x0 <= x1 and x0 > x2) or (x0 >= x1 and x0 < x2) or (x1==x2 and x0==x1 and (((y <= y2 and y >= y1) or (y >= y1 and y <= y2))))):  # 判断x0是否是线段交点的横坐标，x0在左边
                            pNum += 1
                            if x0 == x1 and ((y1 > y2 and y1 > y4) or (y1 < y2 and y1 < y4)):
                                pNum += 1
                    if y2 != y3:
                        x0 = (x2 - x3) / (y2 - y3) * (y - y2) + x2#不必须是x2,y2，只是为了整齐
                        if x >= x0 and ((x0 <= x2 and x0 > x3) or (x0 >= x2 and x0 < x3) or (x3==x2 and x0==x2 and (((y <= y3 and y >= y2) or (y >= y3 and y <= y2))))):
                            pNum += 1
                            if x0 == x2 and ((y2 > y1 and y2 > y3) or (y2 < y1 and y2 < y3)):
                                pNum += 1
                    if y4 != y3:
                        x0 = (x3 - x4) / (y3 - y4) * (y - y3) + x3
                        if x >= x0 and ((x0 < x1 and x0 >= x3) or (x0 > x1 and x0 <= x3 or (x3==x4 and x0==x3 and (((y <= y3 and y >= y4) or (y >= y3 and y <= y4)))))):
                            pNum += 1
                            if x0 == x3 and ((y3 > y4 and y3 > y2) or (y3 < y4 and y3 < y2)):
                                pNum += 1
                    if y1 != y4:
                        x0 = (x1 - x4) / (y1 - y4) * (y - y4) + x4
                        if x >= x0 and ((x0 < x1 and x0 >= x4) or (x0 > x1 and x0 <= x4) or (x1==x4 and x0==x1 and (((y <= y1 and y >= y4) or (y >= y1 and y <= y4))))):
                            pNum += 1
                            if x0 == x4 and ((y4 > y1 and y4 > y3) or (y4 < y3 and y4 < y1)):  # 判断过（xx,yx）是不是算穿过两个点
                                pNum += 1
                    if pNum == 1:
                        if Equation4v[2]==0:
                            continue
                        ztemp = (-Equation4v[i][0] * x - Equation4v[i][1] * y - Equation4v[i][3]) / Equation4v[i][2]
                        if ztemp >= zmax:
                            zmax = ztemp
                            color = QColor(c1, c2, c3)
                    #print("pnum",pNum)
                painter.setPen(QPen(color, 1))
                painter.drawPoint(x, y)
        self.pixLabel.setPixmap(self.pix)
        end_time = time.time()
        print("绘画用时{}秒".format(end_time - start_time))
        self.timeLabel.setText("RayCasting:绘画用时{}秒".format(end_time - start_time))
    def getEquation(self,x1,y1,z1,x2,y2,z2,x3,y3,z3):#求面的方程
        # 通过法向量求平面的方程
        x_1 = x1 - x2
        x_2 = x2 - x3
        y_1 = y1 - y2
        y_2 = y2 - y3
        z_1 = z1 - z2
        z_2 = z2 - z3
        A = y_1 * z_2 - y_2 * z_1
        B = x_2 * z_1 - x_1 * z_2
        C = x_1 * y_2 - x_2 * y_1
        D = -A * x1 - B * y1 - C * z1
        return [A,B,C,D]
    def drawTriangle(self,x1,y1,z1,x2,y2,z2,x3,y3,z3,c1,c2,c3):
        #print("当前函数名为",inspect.currentframe().f_code.co_name)
        #通过法向量求平面的方程
        x_1=x1-x2
        x_2=x2-x3
        y_1 = y1 - y2
        y_2 = y2 - y3
        z_1 = z1 - z2
        z_2 = z2 - z3
        A = y_1 * z_2 - y_2 * z_1
        B = x_2 * z_1 - x_1 * z_2
        C = x_1 * y_2 - x_2 * y_1
        D = -A*x1 - B*y1 - C*z1
        x_list = [x1,x2,x3,x1]
        y_list = [y1, y2, y3, y1]
        painter = QPainter(self.pix)
        painter.setPen(QPen(QColor(int(c1), int(c2), int(c3)), 1))
        # 在QPixmap上进行绘制操作,X扫描线算法
        ymax = int(max(y1,y2,y3))
        ymin = int(min(y1,y2,y3))
        for y in range(ymin,ymax+1):#扫描转换
            point1Finded=False
            for i in range(0,3):
                if (y>=y_list[i] and y<y_list[i+1]) or (y<y_list[i] and y>=y_list[i+1]):#y值在线段范围内
                    if point1Finded==False:
                        p1_x=(x_list[i]-x_list[i+1])/(y_list[i]-y_list[i+1])*(y-y_list[i])+x_list[i]#(x1-x2)/(y1-y2)=(x-x1)/(y-y1)
                        point1Finded = True
                    else:
                        p2_x=(x_list[i]-x_list[i+1])/(y_list[i]-y_list[i+1])*(y-y_list[i])+x_list[i]# (x1-x2)/(y1-y2)=(x-x1)/(y-y1)
                        point1Finded = False
                        for x in range(int(min(p1_x,p2_x)),int(max(p1_x,p2_x))):#+1?
                            if C==0:
                                continue
                            z = (-A * x - B * y - D) / C
                            if z > self.zBuffer[x][y]:
                                self.zBuffer[x][y] = z
                                self.colorBuffer[x][y] = QColor(int(c1), int(c2), int(c3))
                                painter.drawPoint(x, y)
                elif y==y_list[i] and y==y_list[i+1]:
                    for x in range(int(min(x_list[i],x_list[i+1])), int(max(x_list[i],x_list[i+1]))):#for x in range(min(x_list[i],x_list[i+1]), max(x_list[i],x_list[i])+1):
                        if C==0:
                            continue
                        z = (-A * x - B * y - D) / C
                        if z>self.zBuffer[x][y]:
                            print("算出的z",z)
                            self.zBuffer[x][y]=z
                            self.colorBuffer[x][y] = QColor(c1, c2, c3)
                            painter.drawPoint(x, y)
        #painter.end()
        #painter.drawPixmap(0,0,self.pix)
        self.pixLabel.setPixmap(self.pix)
    def drawRect(self,x1,y1,z1,x2,y2,z2,x3,y3,z3,x4,y4,z4,c1,c2,c3):#画凸四边形
        print("当前函数名为",inspect.currentframe().f_code.co_name)
        #通过法向量求平面的方程
        x_1=x1-x2
        x_2=x2-x3
        y_1 = y1 - y2
        y_2 = y2 - y3
        z_1 = z1 - z2
        z_2 = z2 - z3
        A = y_1 * z_2 - y_2 * z_1
        B = x_2 * z_1 - x_1 * z_2
        C = x_1 * y_2 - x_2 * y_1
        D = -A*x1 - B*y1 - C*z1
        x_list = [x1,x2,x3,x4,x1]
        y_list = [y1, y2, y3,y4,y1]
        painter = QPainter(self.pix)
        painter.setPen(QPen(QColor(c1, c2, c3), 1))
        painter.drawPoint(x1,y1)
        painter.drawPoint(x2, y2)
        painter.drawPoint(x3, y3)
        # 在QPixmap上进行绘制操作,X扫描线算法
        ymax = int(max(y1,y2,y3,y4))
        ymin = int(min(y1,y2,y3,y4))

        for y in range(ymin,ymax+1):#扫描转换
            point1Finded=False
            for i in range(0,4):
                if (y>=y_list[i] and y<y_list[i+1]) or (y<y_list[i] and y>=y_list[i+1]):
                    if point1Finded==False:
                        p1_x=(x_list[i]-x_list[i+1])/(y_list[i]-y_list[i+1])*(y-y_list[i])+x_list[i]#(x1-x2)/(y1-y2)=(x-x1)/(y-y1)
                        point1Finded = True
                    else:
                        p2_x=(x_list[i]-x_list[i+1])/(y_list[i]-y_list[i+1])*(y-y_list[i])+x_list[i]# (x1-x2)/(y1-y2)=(x-x1)/(y-y1)
                        point1Finded = False
                        for x in range(int(min(p1_x,p2_x)),int(max(p1_x,p2_x))):
                            z = (-A * x - B * y - D) / C
                            if z >= self.zBuffer[x][y]:
                                self.zBuffer[x][y] = z
                                self.colorBuffer[x][y] = QColor(c1, c2, c3)
                                painter.drawPoint(x, y)
                elif y==y_list[i] and y==y_list[i+1]:
                    for x in range(int(min(x_list[i],x_list[i+1])), int(max(x_list[i],x_list[i])+1)):
                        z = (-A * x - B * y - D) / C
                        if z>=self.zBuffer[x][y]:
                            #print("算出的z",z)
                            self.zBuffer[x][y]=z
                            self.colorBuffer[x][y] = QColor(c1, c2, c3)
                            painter.drawPoint(x, y)
        painter.end()
        #painter.drawPixmap(0,0,self.pix)
        self.pixLabel.setPixmap(self.pix)
        pass
    def drawTriangle0(self,x1,y1,z1,x2,y2,z2,x3,y3,z3,c1,c2,c3):
        print("当前函数名为",inspect.currentframe().f_code.co_name)
        x_list = [x1,x2,x3,x1]
        y_list = [y1, y2, y3, y1]
        painter = QPainter(self.pix)
        painter.setPen(QPen(QColor(c1, c2, c3), 1))
        painter.drawPoint(x1,y1)
        painter.drawPoint(x2, y2)
        painter.drawPoint(x3, y3)
        # 在QPixmap上进行绘制操作,X扫描线算法
        ymax = int(max(y1,y2,y3))
        ymin = int(min(y1,y2,y3))
        for y in range(ymin,ymax+1):#扫描转换
            point1Finded=False
            for i in range(0,3):
                if (y>=y_list[i] and y<y_list[i+1]) or (y<=y_list[i] and y>y_list[i+1]):
                    if point1Finded==False:
                        p1_x=(x_list[i]-x_list[i+1])/(y_list[i]-y_list[i+1])*(y-y_list[i])+x_list[i]#(x1-x2)/(y1-y2)=(x-x1)/(y-y1)
                        point1Finded = True
                    else:
                        p2_x=(x_list[i]-x_list[i+1])/(y_list[i]-y_list[i+1])*(y-y_list[i])+x_list[i]# (x1-x2)/(y1-y2)=(x-x1)/(y-y1)
                        point1Finded = False
                        for x in range(int(min(p1_x,p2_x)),int(max(p1_x,p2_x))):
                                    painter.drawPoint(x, y)
                elif y==y_list[i] and y==y_list[i+1]:
                    for x in range(int(min(x_list[i],x_list[i+1])), int(max(x_list[i],x_list[i])+1)):
                        painter.drawPoint(x, y)
        painter.end()
        #painter.drawPixmap(0,0,self.pix)
        self.pixLabel.setPixmap(self.pix)
        pass
    def drawRect0(self,x1,y1,z1,x2,y2,z2,x3,y3,z3,x4,y4,z4,c1,c2,c3):#画凸四边形
        print("当前函数名为",inspect.currentframe().f_code.co_name)
        x_list = [x1,x2,x3,x4,x1]
        y_list = [y1, y2, y3,y4,y1]
        painter = QPainter(self.pix)
        painter.setPen(QPen(QColor(c1, c2, c3), 1))
        painter.drawPoint(x1,y1)
        painter.drawPoint(x2, y2)
        painter.drawPoint(x3, y3)
        # 在QPixmap上进行绘制操作,X扫描线算法
        ymax = int(max(y1,y2,y3,y4))
        ymin = int(min(y1,y2,y3,y4))
        for y in range(ymin,ymax+1):#扫描转换
            point1Finded=False
            for i in range(0,4):
                if (y>=y_list[i] and y<y_list[i+1]) or (y<=y_list[i] and y>y_list[i+1]):
                    if point1Finded==False:
                        p1_x=(x_list[i]-x_list[i+1])/(y_list[i]-y_list[i+1])*(y-y_list[i])+x_list[i]#(x1-x2)/(y1-y2)=(x-x1)/(y-y1)
                        point1Finded = True
                    else:
                        p2_x=(x_list[i]-x_list[i+1])/(y_list[i]-y_list[i+1])*(y-y_list[i])+x_list[i]# (x1-x2)/(y1-y2)=(x-x1)/(y-y1)
                        point1Finded = False
                        for x in range(int(min(p1_x,p2_x)),int(max(p1_x,p2_x))):
                            painter.drawPoint(x, y)
                elif y==y_list[i] and y==y_list[i+1]:
                    for x in range(int(min(x_list[i],x_list[i+1])), int(max(x_list[i],x_list[i])+1)):
                        painter.drawPoint(x, y)
        painter.end()
        #painter.drawPixmap(0,0,self.pix)
        self.pixLabel.setPixmap(self.pix)
if __name__ == '__main__':
    app = QApplication(sys.argv)
    openGLView = OpenGLView()
    openGLView.show()
    sys.exit(app.exec_())
