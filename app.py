#Import libaries
from flask import Flask, request, render_template, send_file, redirect
import folium
import os
import time
import math
import branca


#Define app and the folder directorys for templates, static and unique maps
app = Flask(__name__, template_folder='templates', static_folder='static')
map_folder = os.path.join(app.root_path, 'cached maps')


#Initilise start and end positions
start_latitude = None
start_longitude = None
start_name = ''

destination_latitude = None
destination_longitude = None
destination_name = ''
#ID used for map name generation
global_id = None
#live_location inisitialise as false
live_location = False
#Google maps average walking speed in kmh
speed = 4.8
#Initilise total distance
result = str()

locations = [
    #LOCATION
    [['Academic and Student Affairs'], [54.58437403687632, -5.933474677076396]],
    [['Administration Building'], [54.58452736772177, -5.93327688374742]],
    [['Ashby Building'], [54.58007433547152, -5.935592059498496]],
    [['Biological Sciences'], [54.57896703662099, -5.936502371659701]],
    [['Canada Room/Council Chamber'], [54.584822375588544, -5.935087425538025]],
    [['Careers, Employability and Skills'], [54.58456772091219, -5.937142952814181]],
    [['Centre for Cancer Research and Cell Biology (CCRCB)'], [54.5861396452996, -5.944647615604617]],
    [['Chrono Centre'], [54.58584299729627, -5.939615333596722]],
    [['Clinical Research Facility'], [54.587753736693344, -5.9422366884135505]],
    [['Computer Science '], [54.58169894475783, -5.9376482843028935]],
    [['Student Wellbeing Service'], [54.58456772091219, -5.937142952814181]],
    [['David Bates Building'], [54.58384686447296, -5.93126108767134]],
    [['David Keir Building'], [54.58117060439069, -5.93602525318017]],
    [['Development and Alumni Relations'], [54.584677822431985, -5.935106200999247]],
    [['Disability Services'], [54.58456772091219, -5.937142952814181]],
    [['Drama and Film Centre at Queens'], [54.58578801013879, -5.9333177531581285]],
    [['Dunluce Health Centre'], [54.5851390128181, -5.942360611702178]],
    [['Elms Village'], [54.57612585412206, -5.94234207851368]],
    [['Elmwood Building'], [54.58510780971737, -5.939348812898065]],
    [['Elmwood Hall'], [54.58420125932277, -5.937357811743834]],
    [['Estates'], [54.58435783719249, -5.933604059531754]],
    [['Finance'], [54.58431078346151, -5.933416856365226]],
    [['Graduate School'], [54.58514430450694, -5.93473703268367]],
    [['Great Hall'], [54.58454881219248, -5.935079378911786]],
    [['Harty Room'], [54.585011418634664, -5.93316569502097]],
    [['Health Sciences Building'], [54.58660702320403, -5.946585803378913]],
    [['Human Resources'], [54.58419837710644, -5.933606314991591]],
    [['Information Services'], [54.58380395735038, -5.932364910656428]],
    [['Institute of Professional Legal Studies (IPLS)'], [54.579023995281226, -5.9377396107889195]],
    [['International Office'], [54.584436899364654, -5.935141069712947]],
    [['INTO Queens'], [54.57930335140277, -5.93808936622602]],
    [['Lanyon Building'], [54.58448404740997, -5.935159301057353]],
    [['Main Site Tower'], [54.584731476918904, -5.934128091650716]],
    [['Marketing, Recruitment,Communications and Internationalisation'], [54.58438560588251, -5.935194713887871]],
    [['McClay Research Centre'], [54.58642033705481, -5.943106386337827]],
    [['Medical Biology Centre (MBC)'], [54.58617988511076, -5.942385666388259]],
    [['Naughton Gallery at Queens'], [54.58432032316817, -5.9350927899592785]],
    [['New Physics Building'], [54.58379684096096, -5.934594062197901]],
    [['Northern Ireland Technology Centre (NITC)'], [54.58042280920047, -5.93707170772201]],
    [['Occupational Health and Safety Services'], [54.578523068300605, -5.937947913574511]],
    [['Old Physics Building'], [54.58376844134731, -5.9348406585386035]],
    [['Peter Froggatt Centre (PFC)'], [54.58470105949851, -5.9334766034009006]],
    [['Pharmacy Building'], [54.586329469218455, -5.942700637129458]],
    [['Physical Education Centre (PEC)'], [54.58109000876869, -5.929670225916936]],
    [['Queens Film Theatre (QFT)'], [54.58546208738367, -5.933957111506692]],
    [['Registrar and Chief Operating Officer'], [54.58416955080209, -5.9354173372175625]],
    [['Research and Enterprise'], [54.585498286277655, -5.936380984511049]],
    [['Riddel Hall'], [54.57617620692349, -5.934829401341759]],
    [['Sonic Arts Research Centre (SARC)'], [54.580530653927234, -5.93777668187978]],
    [['South Dining Hall'], [54.58375784064992, -5.935614140012404]],
    [['Student Plus '], [54.58421618149038, -5.935216171561602]],
    [['One Elmwood, Student Centre and Students Union'], [54.58455626384715, -5.937126707190225]],
    [['The McClay Library'], [54.5838034291948, -5.932109316417613]],
    [['University Health Centre'], [54.58398355243926, -5.937445814805631]],
    [['Vice-Chancellors Office'], [54.58433897538085, -5.93529395561524]],
    [['Welcome Centre'], [54.58450009692936, -5.935297021020948]],
    [['Whitla Hall'], [54.58371597203839, -5.9360391443710725]],
    [['Whitla Medical Building'], [54.5859453835362, -5.9435628928809185]],
    [['Wellcome-Wolfson Institute for Experimental Medicine'], [54.5861396452996, -5.944647615604617]],
    #FACULTY OFFICES
    [['Arts, Humanities and Social Sciences'], [54.58629381455676, -5.935567924057082]],
    [['Engineering and Physical Sciences'], [54.58242405458074, -5.937056795100541]],
    [['Medicine, Health and Life Sciences'], [54.585059641312405, -5.940966659119539]],
    #SCHOOL OFFICES
    [['Arts, English and Languages'], [54.58576124307094, -5.935888914346184]],
    [['Chemistry and Chemical Engineering'], [54.581204721059905, -5.936039256622704]],
    [['Electronics, Electrical Engineering and Computer Science'], [54.58187878256887, -5.937437179303816]],
    [['History, Anthropology, Philosophy and Politics'], [54.585402408695174, -5.93325601720141]],
    [['Law'], [54.5850675194871, -5.93413954461042]],
    [['Mathematics and Physics'], [54.583925853581356, -5.9345350535844466]],
    [['Mechanical and Aerospace Engineering'], [54.579998106495864, -5.935939683956971]],
    [['Medicine, Dentistry and Biomedical Sciences'], [54.58585422196802, -5.9436704858119045]],
    [['Natural and Built Environment'], [54.58109995799967, -5.935992882063089]],
    [['Nursing and Midwifery'], [54.58588956241748, -5.943127866735547]],
    [['Pharmacy'], [54.5863775945713, -5.942859623121422]],
    [['Psychology'], [54.58116272803322, -5.937930621647734]],
    [['Queens Business School'], [54.57628570307882, -5.935233726404529]],
    [['Social Sciences, Education and Social Work'], [54.58576463882744, -5.931447405599344]],
    #GLOBAL RESEARCH INSTITUTES
    [['The Senator George J Mitchell Institute for Global Peace, Security and Justice'], [54.585487641335426, -5.934184670309235]],
    [['The William J Clinton Leadership Institute'], [54.57617014154859, -5.935100555729443]],
    [['The Institute for Global Food Security'], [54.580479444858256, -5.9373473784700375]],
    [['The Institute of Electronics, Communications and Information Technology (Titanic Quarter)'], [54.614029465909745, -5.89993074581833]],
    [['The Institute of Health Sciences'], [54.58663012747263, -5.946840979530259]],
    [[''], [0, 0]]
]



road_network = [
    [[82, 6, 15, 16, 17], [54.58319268940053, -5.936868755846738]],#1
    [[82, 3, 158], [54.58062727493786, -5.9384974272965305]],#2
    [[2, 4, 81], [54.58013316280848, -5.938840257172553]],#3
    [[3, 83, 140], [54.57948218053235, -5.9392191744718845]],#4
    [[83, 127], [54.576698993144056, -5.943285556184135]],#5
    [[1, 7], [54.58196226110681, -5.936112250889515]],#6
    [[6, 8, 84, 179], [54.581094873565284, -5.935709919525995]],#7
    [[7, 9, 85], [54.580690708199576, -5.935522164913764]],#8
    [[8, 10, 86, 113], [54.58027410276947, -5.935318316978107]],#9
    [[9, 11, 87, 80], [54.57973223040577, -5.935038099626508]],#10
    [[10, 12, 153], [54.58056852502558, -5.932376157474399]],#11
    [[86, 11, 13], [54.58099134536095, -5.932746302325432]],#12
    [[85, 12, 14], [54.581364418472845, -5.933127175995637]],#13
    [[84, 13], [54.58172816147086, -5.933449041070028]],#14
    [[1, 18, 69], [54.58350952262024, -5.937992703086964]],#15
    [[1, 21], [54.5838390503475, -5.936662327448796]],#16
    [[1, 40, 153], [54.58317377464968, -5.934162508634634]],#17
    [[15, 19], [54.58382972413695, -5.937735211049029]],#18
    [[18, 20, 79], [54.58394474736421, -5.938067804958222]],#19
    [[19, 22, 60], [54.584473228288886, -5.937633287109115]],#20
    [[16, 22], [54.58410950979972, -5.936549674695294]],#21
    [[20, 21, 24], [54.584224532246665, -5.93656040352842]],#22
    [[87, 157], [54.57678688991813, -5.93341412072522]],#23
    [[22, 26, 28, 120, 161, 115, 124], [54.58460442225688, -5.93642679210324]],#24
    [[21, 26, 159, 165, 176], [54.5840572907009, -5.935756239866964]],#25
    [[24, 25, 27, 110], [54.584536031214206, -5.935638222673378]],#26
    [[30, 32], [54.58504896124082, -5.935477290133882]],#27
    [[24, 29], [54.585167089664274, -5.936292681653193]],#28
    [[28, 30, 41, 156], [54.58553079871585, -5.936163935622153]],#29
    [[27, 29, 31], [54.58545308338017, -5.935391459445962]],#30
    [[30, 33, 154, 185, 175], [54.58535535434734, -5.934110909297717]],#31
    [[27, 175, 142], [54.58492772382242, -5.9342756605248]],#32
    [[31, 34, 49, 134, 174], [54.585172472486846, -5.932542502738583]],#33
    [[33, 35, 36, 134], [54.5848647161818, -5.9325961469174855]],#34
    [[34, 37], [54.584659544017555, -5.93266051993775]],#35
    [[34, 38], [54.584746586881856, -5.9314857124121145]],#36
    [[35, 39, 136, 137], [54.584141450791265, -5.932745593447676]],#37
    [[36, 37, 121, 162], [54.58406062408273, -5.931651252198073]],#38
    [[37, 40, 137, 176], [54.58384612165577, -5.932831424133919]],#39
    [[17, 39], [54.58353835532619, -5.933046000856088]],#40
    [[29, 42, 56, 171], [54.58584191656101, -5.936091391990145]],#41
    [[41, 43, 46], [54.58614745169782, -5.935962422637057]],#42
    [[42, 44, 55], [54.58644858841691, -5.935913110817893]],#43
    [[43, 45, 90, 53], [54.58709481588647, -5.935810693978281]],#44
    [[44, 52, 61], [54.58765750900321, -5.935647585679379]],#45
    [[42, 47, 88], [54.586145460021726, -5.935274763930268]],#46
    [[46, 48, 50], [54.58617623321975, -5.932236397629112]],#47
    [[89, 47, 49, 184], [54.585664076262134, -5.932365366982201]],#48
    [[33, 48], [54.585523396829004, -5.9323957127123395]],#49
    [[47, 51], [54.586771909830816, -5.932407092364397]],#50
    [[50, 52], [54.58800060270836, -5.9329874544583205]],#51
    [[91, 45, 51], [54.58787531729787, -5.933848514550995]],#52
    [[44, 54, 62], [54.58723789432776, -5.937232063547173]],#53
    [[53, 55, 57, 63], [54.58680488061528, -5.937459656533367]],#54
    [[43, 54, 56], [54.58656309431035, -5.936458247438804]],#55
    [[41, 55, 57], [54.58589487741139, -5.936625148947561]],#56
    [[54, 56, 58], [54.5861454600287, -5.937812425639222]],#57
    [[57, 59, 64], [54.586444398682, -5.93906418703733]],#58
    [[58, 65, 117], [54.58602896128083, -5.9395914441142725]],#59
    [[20, 67, 79, 128], [54.58519147934766, -5.9403197416541715]],#60
    [[45, 99], [54.58831031120545, -5.935272057271284]],#61
    [[53, 61], [54.587549408290776, -5.937622668058093]],#62
    [[54, 62], [54.587094724131966, -5.938719925550254]],#63
    [[58, 63, 92], [54.58659937139167, -5.93954924806023]],#64
    [[59, 64, 66], [54.5861964307649, -5.940104256201519]],#65
    [[65, 67, 70], [54.585851324031495, -5.940513260442642]],#66
    [[60, 66, 68, 170, 72], [54.58540730495848, -5.941067070017666]],#67
    [[67, 69, 170], [54.58505493769983, -5.941566285645488]],#68
    [[15, 68], [54.584747196207694, -5.942059403760234]],#69
    [[66, 71, 76], [54.58603090251223, -5.94104282180928]],#70
    [[70, 72], [54.58564403638564, -5.941323519813058]],#71
    [[71, 73, 67], [54.58535828063777, -5.941520767058957]],#72
    [[72, 74, 68, 126], [54.58514725972199, -5.941831810792874]],#73
    [[73, 75, 180], [54.58559128162923, -5.94347048022034]],#74
    [[74, 167, 178], [54.58571877217367, -5.943887734009742]],#75
    [[70, 77, 92, 145, 152], [54.58632104969627, -5.94208974949905]],#76
    [[76, 78, 166, 144], [54.5866463637786, -5.943311165137115]],#77
    [[92, 77, 118], [54.587301380207606, -5.942764941998767]],#78
    #Added for better roads
    [[60, 19], [54.584739765530195, -5.940698108954276]],#79
    [[10, 81, 109, 149], [54.57908623937899, -5.936620134038731]],#80
    [[3, 80], [54.57992308461903, -5.938171705716185]],#81
    [[1, 2, 119, 182], [54.58155448809072, -5.938094864461151]],#82
    [[4, 5], [54.578575858305385, -5.939723937744051]],#83
    [[7, 14], [54.581202422575856, -5.935108300255299]],#84
    [[8, 13], [54.58078263972547, -5.9349411486632]],#85
    [[9, 12], [54.58036554349766, -5.934713636762237]],#86
    [[10, 23], [54.57862240290512, -5.934181845140737]],#87
    [[89, 46], [54.58587659948718, -5.935246443048482]],#88
    [[88, 48, 125], [54.585858115731476, -5.933160378120435]],#89
    [[44, 91], [54.58703527933091, -5.9355750775763605]],#90
    [[90, 52], [54.58720007174561, -5.9336263090465415]],#91
    [[64, 78, 76], [54.58698053917059, -5.941624079766755]],#92
    [[18, 94], [54.583783037782815, -5.937520248283547]],#93
    [[93, 16, 163, 129], [54.58400197071235, -5.937274403175693]],#94
    [[59, 28], [54.585299558986506, -5.937265511195161]],#95
    [[32, 134], [54.584831619591824, -5.933181797200551]],#96
    [[96, 35, 112, 151], [54.584676186104666, -5.933128153025629]],#97
    [[43, 50, 168], [54.586386012961114, -5.93574750481616]],#98
    #Titanic
    [[61, 100], [54.593509457526835, -5.931132178157443]],#99
    [[99, 101], [54.595962004668316, -5.93139770330602]],#100
    [[100, 102], [54.59637507449447, -5.921317878608474]],#101
    [[101, 103], [54.600198604901024, -5.921507539407051]],#102
    [[102, 104], [54.60032604972925, -5.9192391960792134]],#103
    [[103, 105], [54.60256516943375, -5.918495370965981]],#104
    [[104, 106], [54.605296068720044, -5.915860082772903]],#105
    [[105, 107], [54.60435546753285, -5.913424185911486]],#106
    [[106, 108], [54.613624547044715, -5.900027458522031]],#107
    [[107], [54.614029465909745, -5.89993074581833]],#108 #The Institute of Electronics, Communications and Information Technology (Titanic Quarter)
    #BUILDINGS ETC//
    [[80], [54.57896703662099, -5.936502371659701]],#109 Biological Sciences
    [[26, 141], [54.58450009692936, -5.935297021020948]],#110 Welcome Centre
    [[112, 130, 131], [54.58437403687632, -5.933474677076396]],#Academic and Student Affairs #111
    [[97, 111], [54.58452736772177, -5.93327688374742]],#Administration Building #112
    [[9, 177], [54.58007433547152, -5.935592059498496]],#Ashby Building #113
    [[123], [54.584822375588544, -5.935087425538025]],#Canada Room/Council Chamber #114
    [[24], [54.58456772091219, -5.937142952814181]],#Careers, Employability and Skills #115
    [[167, 135], [54.5861396452996, -5.944647615604617]],#Centre for Cancer Research and Cell Biology (CCRCB)  #116
    [[59], [54.58584299729627, -5.939615333596722]],#Chrono Centre #117
    [[78], [54.587753736693344, -5.9422366884135505]],#Clinical Research Facility #118
    [[82, 173], [54.58169894475783, -5.9376482843028935]],#Computer Science  #119
    [[24], [54.58472469401339, -5.936857679361971]],#Student Wellbeing Service #120
    [[38], [54.58384686447296, -5.93126108767134]],#David Bates Building #121
    [[179, 172], [54.58117060439069, -5.93602525318017]],#David Keir Building #122
    [[133, 114], [54.584677822431985, -5.935106200999247]],#Development and Alumni Relations #123
    [[24], [54.5848057301377, -5.936824975191787]],#Disability Services #124
    [[89], [54.58578801013879, -5.9333177531581285]],#Drama and Film Centre at Queens #125
    [[73], [54.5851390128181, -5.942360611702178]],#Dunluce Health Centre #126
    [[5], [54.57612585412206, -5.94234207851368]],#Elms Village #127
    [[60], [54.58510780971737, -5.939348812898065]],#Elmwood Building #128
    [[94], [54.58420125932277, -5.937357811743834]],#Elmwood Hall #129
    [[111, 136], [54.58435783719249, -5.933604059531754]],#Estates #130
    [[111, 136], [54.58431078346151, -5.933416856365226]],#Finance #131
    [[175], [54.58514430450694, -5.93473703268367]],#Graduate School #132
    [[110, 123], [54.58454881219248, -5.935079378911786]],#Great Hall #133
    [[33, 34, 96], [54.585011418634664, -5.93316569502097]],#Harty Room #134
    [[116, 188], [54.58660702320403, -5.946585803378913]],#Health Sciences Building #135
    [[37, 130, 131], [54.58419837710644, -5.933606314991591]],#Human Resources #136
    [[37, 39, 162], [54.58380395735038, -5.932364910656428]],#Information Services #137
    [[140, 149], [54.57890534318588, -5.9378337586596714]],#Institute of Professional Legal Studies (IPLS) #138
    [[110, 143], [54.584436899364654, -5.935141069712947]],#International Office #139
    [[4, 138], [54.57937213347253, -5.938389753728512]],#INTO Queens #140
    [[110, 133, 139], [54.58448404740997, -5.935159301057353]],#Lanyon Building #141
    [[32], [54.584731476918904, -5.934128091650716]],#Main Site Tower #142
    [[139, 146, 164], [54.58438560588251, -5.935194713887871]],#Marketing, Recruitment,Communications and Internationalisation #143
    [[77, 181], [54.58642033705481, -5.943106386337827]],#McClay Research Centre #144
    [[76], [54.58617988511076, -5.942385666388259]],#Medical Biology Centre (MBC) #145
    [[143, 160], [54.58432032316817, -5.9350927899592785]],#Naughton Gallery at Queens #146
    [[150, 176], [54.58379684096096, -5.934594062197901]],#New Physics Building #147
    [[187], [54.58042280920047, -5.93707170772201]],#Northern Ireland Technology Centre (NITC) #148
    [[80, 138], [54.57857604350641, -5.937865257134043]],#Occupational Health and Safety Services #149
    [[159, 147], [54.58376844134731, -5.9348406585386035]],#Old Physics Building #150
    [[97], [54.58470105949851, -5.9334766034009006]],#Peter Froggatt Centre (PFC) #151
    [[76, 181], [54.586329469218455, -5.942700637129458]],#Pharmacy Building #152 
    [[11, 17], [54.58109000876869, -5.929670225916936]],#Physical Education Centre (PEC) #153
    [[31], [54.58546208738367, -5.933957111506692]],#Queens Film Theatre (QFT) #154
    [[160], [54.58416955080209, -5.9354173372175625]],#Registrar and Chief Operating Officer #155
    [[29], [54.585498286277655, -5.936380984511049]],#Research and Enterprise #156
    [[23, 186], [54.57617620692349, -5.934829401341759]],#Riddel Hall #157
    [[2, 187], [54.580530653927234, -5.93777668187978]],#Sonic Arts Research Centre (SARC) #158
    [[25, 165, 150], [54.58375784064992, -5.935614140012404]],#South Dining Hall #159
    [[164, 146, 155], [54.58421618149038, -5.935216171561602]],#Student Plus #160
    [[24], [54.58460117896461, -5.936993006949371]],#One Elmwood, Student Centre and Students Union #161
    [[38, 137], [54.5838034291948, -5.932109316417613]],#The McClay Library #162
    [[94], [54.58398355243926, -5.937445814805631]],#University Health Centre #163
    [[143, 160], [54.58433897538085, -5.93529395561524]],#Vice-Chancellors Office #164
    [[25, 159], [54.58371597203839, -5.9360391443710725]],#Whitla Hall #165
    [[178, 77], [54.5859453835362, -5.9435628928809185]],#Whitla Medical Building #166
    [[75, 116], [54.585997517261205, -5.944159030516546]],#Wellcome-Wolfson Institute for Experimental Medicine #167
    #FACULTY OFFICES
    [[98], [54.58629381455676, -5.935567924057082]],#Arts, Humanities and Social Sciences #168
    [[173], [54.58242405458074, -5.937056795100541]],#Engineering and Physical Sciences #169
    [[67, 68], [54.585059641312405, -5.940966659119539]],#Medicine, Health and Life Sciences #170
    #SCHOOL OFFICES  
    [[41], [54.58576124307094, -5.935888914346184]],#Arts, English and Languages #171
    [[122], [54.581204721059905, -5.936039256622704]],#Chemistry and Chemical Engineering #172
    [[119, 169], [54.58187878256887, -5.937437179303816]],#Electronics, Electrical Engineering and Computer Science #173
    [[33], [54.585402408695174, -5.93325601720141]],#History, Anthropology, Philosophy and Politics #174
    [[31, 32, 132], [54.5850675194871, -5.93413954461042]],#Law #175
    [[147, 25, 39], [54.583925853581356, -5.9345350535844466]],#Mathematics and Physics #176
    [[113], [54.579998106495864, -5.935939683956971]],#Mechanical and Aerospace Engineering #177
    [[75, 166], [54.58585422196802, -5.9436704858119045]],#Medicine, Dentistry and Biomedical Sciences #178
    [[7, 122], [54.58109995799967, -5.935992882063089]],#Natural and Built Environment #179
    [[74], [54.58588956241748, -5.943127866735547]],#Nursing and Midwifery #180
    [[144, 152], [54.5863775945713, -5.942859623121422]],#Pharmacy #181
    [[82], [54.58116272803322, -5.937930621647734]],#Psychology #182
    [[186], [54.57628570307882, -5.935233726404529]],#Queens Business School #183
    [[48], [54.58576463882744, -5.931447405599344]],#Social Sciences, Education and Social Work #184
#GLOBAL RESEARCH INSTITUTES
    [[31], [54.585487641335426, -5.934184670309235]],#The Senator George J Mitchell Institute for Global Peace, Security and Justice #185
    [[157, 183], [54.57617014154859, -5.935100555729443]],#The William J Clinton Leadership Institute #186
    [[148, 158], [54.580479444858256, -5.9373473784700375]],#The Institute for Global Food Security #187
    [[135], [54.58663012747263, -5.946840979530259]]#The Institute of Health Sciences #188
]



room_numbers = [
    [[54.580530653927234, -5.93777668187978], [[[-1], ["LG008", "LG009", "LG0010", "LG018", "LG021", "LG022", "LG023", "LG024", "LG025", "LG026", "LG029", "LG030", "LG031", "LG032"]]]]
    ]




#Time since epoch, used to generate a random file name for the map
def millisecondsSinceEpoch():
    return int(time.time() * 1000) #*1000 to turn into milliseconds

#Clean up old files
def deleteOldMapFiles():
    current_time = time.time()
    one_day_ago = current_time - 24 #* 60 * 60  # 24 hours ago
    for root, dirs, files in os.walk(map_folder):
        for file in files:
            file_path = os.path.join(root, file)
            file_creation_time = os.path.getctime(file_path)
            if file_creation_time < one_day_ago:
                os.remove(file_path)
                print('file deleted')

#find distance between the nodes
def haversineDistance(lat1, long1, lat2, long2):
    #Convert latitude and longitude from degrees to radians
    lat1 = math.radians(lat1)
    long1 = math.radians(long1)
    lat2 = math.radians(lat2)
    long2 = math.radians(long2)
    #Haversine formula
    distance = math.acos(math.sin(lat1) * math.sin(lat2) + math.cos(lat1) * math.cos(lat2) * math.cos(long2 - long1))
    #Convert the result from radians to the desired distance unit (e.g., kilometers or miles)
    radius_of_earth = 6371
    distance_in_km = radius_of_earth * distance
    return distance_in_km

#dijkstra algorithm
def dijkstra(start_node, end_node):
    distances = {node: float('inf') for node in range(1, len(road_network) + 1)}
    previous_nodes = {node: None for node in range(1, len(road_network) + 1)}
    distances[start_node] = 0
    visited = set()
    unvisited_nodes = set(range(1, len(road_network) + 1))
    while unvisited_nodes:
        current_node = min(unvisited_nodes, key=lambda node: distances[node])
        unvisited_nodes.remove(current_node)
        for neighbor in road_network[current_node - 1][0]:
            if neighbor not in visited:
                distance = distances[current_node] + haversineDistance(*road_network[current_node - 1][1], *road_network[neighbor - 1][1])
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous_nodes[neighbor] = current_node
        visited.add(current_node)
    path = [] 
    current = end_node
    total_distance = 0
    while current is not None:
        path.insert(0, current)
        if previous_nodes[current] is not None:
            total_distance += haversineDistance(*road_network[current - 1][1], *road_network[previous_nodes[current] - 1][1])
        current = previous_nodes[current]
    return path, total_distance

#find what node is used from the start and end coordinates
def coordinateOfNode(road_network, latitude, longitude):
    for entry in road_network:
        if entry[1] == [latitude, longitude]:
            return road_network.index(entry)
    return None

#Function for floos and room numbers
def floorsAndRooms(destination_latitude, destination_longitude, result):
    global room_numbers
    #Getting the data for each entry
    for entry in room_numbers:
        coordinates = entry[0]
        rooms_info = entry[1]
        #Check if the current entry's coordinates match the destination
        if coordinates[0] == destination_latitude and coordinates[1] == destination_longitude:
            #Displaying floor and room information
            result += "<table>"
            result += "<tr><th>floor&nbsp;</th><th>&nbsp;rooms</th></tr>"
            for floor, rooms in rooms_info:
                floor_number = floor[0]
                room_numbers_str = ', '.join(map(str, rooms))
                result += f"<tr><td>{floor_number}</td><td>{room_numbers_str}</td></tr>"
            result += "</table>"
    return result






#Function to get the live location
@app.route('/get_location', methods=['POST'])
def get_location():
    global start_latitude, start_longitude, live_location
    data = request.get_json()
    user_location = data.get('location')
    #Store the user's location coordinates in the global variables
    start_latitude = user_location['latitude']
    start_longitude = user_location['longitude']
    live_location = True
    #Flask always wants you to return something
    return ('', 204)


@app.route('/set', methods=['POST'])
def set_location():
    global start_latitude, start_longitude, start_name, destination_latitude, destination_longitude, destination_name
    if request.method == 'POST':
        start_name = request.form['location']
        print(start_name)
        destination_name = request.form['destination']
        print(destination_name)
        if start_name == '':
            for destination in locations:
                if destination[0][0] == destination_name:
                    destination_latitude, destination_longitude = destination[1]
                    print(destination_latitude, destination_longitude)
                    break
        else:
            for location in locations:
                if location[0][0] == start_name:
                    start_latitude, start_longitude = location[1]
                    print(start_latitude, start_longitude)
                    break
            for destination in locations:
                if destination[0][0] == destination_name:
                    destination_latitude, destination_longitude = destination[1]
                    print(destination_latitude, destination_longitude)
                    break
    return redirect('/Mymap')


    
#Home route
@app.route('/')
def home():
    deleteOldMapFiles()
    return render_template('home.html')

#Location route
@app.route('/location')
def location():
    deleteOldMapFiles()
    return render_template('Geo.html', locations=locations)

#Show map with every point route
@app.route('/wholemap')
def wholeMap():
    return render_template('wholeMap.html')

#Map route
@app.route('/Mymap')
def Mymap():
    deleteOldMapFiles()
    #Location
    global start_latitude, start_longitude, destination_latitude, destination_longitude, global_id, start_name, destination_name, live_location, speed
    #Create a new map centred around the location
    campus_map = folium.Map(location=[start_latitude, start_longitude], zoom_start=15, zoom_control=False, max_bounds=True)
    
    #Function to join live location onto the map network
    def find_closest_node(latitude, longitude):
        closest_node = None
        min_distance = float('inf')
        for i, node_info in enumerate(road_network):
            node_coords = node_info[1]
            distance = haversineDistance(latitude, longitude, node_coords[0], node_coords[1])
            if distance < min_distance:
                closest_node = i + 1  #Adjust for the array index starting from 1
                min_distance = distance
        return closest_node

    if live_location == True:
        start = find_closest_node(start_latitude, start_longitude)
        end = coordinateOfNode(road_network, destination_latitude, destination_longitude)
        #Adjusment for the array
        end = end + 1
        coords1 = [start_latitude, start_longitude]
        coords2 = road_network[start - 1][1]
        folium.PolyLine(locations=[coords1, coords2], color='blue').add_to(campus_map)


    elif live_location == False:
        start = coordinateOfNode(road_network, start_latitude, start_longitude)
        end = coordinateOfNode(road_network, destination_latitude, destination_longitude)
        #Adjusment for the array
        start = start + 1
        end = end + 1
    
    print(start)
    print(end)
    path, total_distance = dijkstra(start, end)
    #Round total_distnace to 2 decimal places
    total_distance = round(total_distance, 2)
    
    #Total time rounded to 1 decimal places
    total_time = round(((total_distance / speed) * 60), 1)

    #Add lines to represent road connections in the shortest path
    for i in range(len(path) - 1):
        current_node = path[i]
        next_node = path[i + 1]
        coords1 = road_network[current_node - 1][1]
        coords2 = road_network[next_node - 1][1]
        folium.PolyLine(locations=[coords1, coords2], color='blue').add_to(campus_map)

    #Getting floor and room numbers of destination
    RoomAndFloor = floorsAndRooms(destination_latitude, destination_longitude, result)
 
    #Adding markers for location and desitnation 
    folium.Marker([start_latitude, start_longitude], popup='Your location').add_to(campus_map)
    folium.Marker([destination_latitude, destination_longitude], popup=folium.Popup(RoomAndFloor, max_width=300)).add_to(campus_map)

    #Generate the file name
    global_id = millisecondsSinceEpoch()
    html_filename = f'{global_id}.html'
    html_file_path = os.path.join(map_folder, html_filename)

    #Save the destination and current location to the map
    campus_map.save(html_file_path)

    #Adding navigation bar to the generated map
    #Read the content of navbar.html
    navbar_file_path = os.path.join('templates', 'navbar.html')
    with open(navbar_file_path, 'r') as navbar_file:
        navbar_contents = navbar_file.read()
    #Add total distance to the navbar
    navbar_contents = navbar_contents.replace('{{ total_distance }}', f'Distance to destination: {total_distance} km')
    #Add total time to the navbar
    navbar_contents = navbar_contents.replace('{{ total_time }}', f'Time to reach destination: {total_time} minutes')
    
    #Read the content of the generated map and add navbar to the top of the generated map page
    with open(html_file_path, 'r') as map_file:
        map_contents = map_file.read()
        combined_contents = navbar_contents + map_contents
    #Save the combined content to the global_id file
    with open(html_file_path, 'w') as destination_file:
        destination_file.write(combined_contents)

    #Set live_location as false for next time
    live_location = False
    
    #Render the map
    return send_file(os.path.join(map_folder, html_filename))



if __name__ == '__main__':
    #Start the Flask app 
    app.run(host='0.0.0.0', port=443, debug=True, ssl_context='adhoc')
