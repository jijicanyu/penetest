#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymysql
import os
import sys
import pickle
import time

HOST = '127.0.0.1'
USER = 'root'
PASSWD = 'root'
DATABASE = 'mydata'
PORT = '3306'
CHARSET = 'utf8'
SPHINX = r'/mnt/sphinx'    #sphinx文件夹路径
PHP = r'/var/www/html'	#php网页根目录
SOURCE = None   #存储第一个source的名字
MEM_LIMIT = '256M'  #indexer中的mem_limit
FIRST_COLUMN = {'csdn':'id',
                'sgk':'id',
                'tgbus':'id'}
                
#连接数据库
conn = pymysql.connect(host=HOST,user=USER,passwd=PASSWD,db=DATABASE,charset=CHARSET)
cur = conn.cursor()

#取得所有表名
table_len = cur.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = '" + DATABASE + "';")
if table_len == 0:
    cur.close()
    conn.close()
    sys.exit()

#加载table_id字典
try:
    with open(SPHINX + r"/mysql.pickle","rb") as tmp:
        table_id = pickle.load(tmp)
except (FileNotFoundError,EOFError):
    table_id = dict()

#扩充table_id列表
table_name = list(table_id.values())
old_table_len = len(table_id)   #记录之前已经索引的数目
for table in cur:
    #去除已有的键
    if table[0] in table_name:
        continue
    #添加数据
    table_id[len(table_id)+1] = table[0]

#打开mysql.conf写数据
with open(SPHINX + r"/mysql.conf","w",encoding="utf-8") as conf:
    #写source源定义部分
    #第一个source
    conf.write("source " + table_id[1] + "\n{\n")
    conf.write("    type = mysql\n\n")
    conf.write("    sql_host = " + HOST + "\n")
    conf.write("    sql_user = " + USER + "\n")
    conf.write("    sql_pass = " + PASSWD + "\n")
    conf.write("    sql_db = " + DATABASE + "\n")
    conf.write("    sql_port = " + PORT + "\n")
    conf.write("    sql_query_pre = SET NAMES " + CHARSET + "\n\n")
    #打印前两列
    conf.write("    sql_query = SELECT `" + FIRST_COLUMN[table_id[1]] + "`,1 AS `table_id`")
    #读取列
    cur.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = '" + DATABASE + "' and TABLE_NAME = '" + table_id[1] + "';")
    #打印剩余列
    for column in cur:
        if column[0] == FIRST_COLUMN[table_id[1]]:
            continue
        conf.write(",`" + column[0] + "`")
    conf.write(" FROM `" + table_id[1] + "`\n")
    conf.write("    sql_attr_uint = table_id\n}\n\n")
    #打印剩余source
    for no in range(2,len(table_id)+1):
        conf.write("source " + table_id[no] + " : " + table_id[1] + "\n{\n")
        conf.write("    sql_query = SELECT `" + FIRST_COLUMN[table_id[no]] + "`," + str(no) + " AS `table_id`")
        #读取列
        cur.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = '" + DATABASE + "' and TABLE_NAME = '" + table_id[no] + "';")
        #打印剩余列
        for column in cur:
            if column[0] == FIRST_COLUMN[table_id[no]]:
                continue
            conf.write(",`" + column[0] + "`")
        conf.write(" FROM `" + table_id[no] + "`\n")
        conf.write("}\n\n")
    #写index部分
    #第一个index
    conf.write("index " + table_id[1] + "\n{\n")
    conf.write("    source = " + table_id[1] + "\n")
    conf.write("    path = " + SPHINX + "/data/" + table_id[1] + "\n")
    conf.write("    docinfo = extern\n")
    conf.write("    mlock = 0\n")
    conf.write("    morphology = none\n")
    conf.write("    min_word_len = 1\n")
    conf.write("    html_strip = 0\n")
    conf.write(r'''    charset_table = U+FF10..U+FF19->0..9, U+FF21..U+FF3A->a..z, U+FF41..U+FF5A->a..z, 0..9, A..Z->a..z, a..z, \
        U+F900->U+8C48, U+F901->U+66F4, U+F902->U+8ECA, U+F903->U+8CC8, U+F904->U+6ED1, U+F905->U+4E32, U+F906->U+53E5, \
        U+F907->U+9F9C, U+F908->U+9F9C, U+F909->U+5951, U+F90A->U+91D1, U+F90B->U+5587, U+F90C->U+5948, U+F90D->U+61F6, U+F90E->U+7669, \
        U+F90F->U+7F85, U+F910->U+863F, U+F911->U+87BA, U+F912->U+88F8, U+F913->U+908F, U+F914->U+6A02, U+F915->U+6D1B, U+F916->U+70D9, \
        U+F917->U+73DE, U+F918->U+843D, U+F919->U+916A, U+F91A->U+99F1, U+F91B->U+4E82, U+F91C->U+5375, U+F91D->U+6B04, U+F91E->U+721B, \
        U+F91F->U+862D, U+F920->U+9E1E, U+F921->U+5D50, U+F922->U+6FEB, U+F923->U+85CD, U+F924->U+8964, U+F925->U+62C9, U+F926->U+81D8, \
        U+F927->U+881F, U+F928->U+5ECA, U+F929->U+6717, U+F92A->U+6D6A, U+F92B->U+72FC, U+F92C->U+90CE, U+F92D->U+4F86, U+F92E->U+51B7, \
        U+F92F->U+52DE, U+F930->U+64C4, U+F931->U+6AD3, U+F932->U+7210, U+F933->U+76E7, U+F934->U+8001, U+F935->U+8606, U+F936->U+865C, \
        U+F937->U+8DEF, U+F938->U+9732, U+F939->U+9B6F, U+F93A->U+9DFA, U+F93B->U+788C, U+F93C->U+797F, U+F93D->U+7DA0, U+F93E->U+83C9, \
        U+F93F->U+9304, U+F940->U+9E7F, U+F941->U+8AD6, U+F942->U+58DF, U+F943->U+5F04, U+F944->U+7C60, U+F945->U+807E, U+F946->U+7262, \
        U+F947->U+78CA, U+F948->U+8CC2, U+F949->U+96F7, U+F94A->U+58D8, U+F94B->U+5C62, U+F94C->U+6A13, U+F94D->U+6DDA, U+F94E->U+6F0F, \
        U+F94F->U+7D2F, U+F950->U+7E37, U+F951->U+964B, U+F952->U+52D2, U+F953->U+808B, U+F954->U+51DC, U+F955->U+51CC, U+F956->U+7A1C, \
        U+F957->U+7DBE, U+F958->U+83F1, U+F959->U+9675, U+F95A->U+8B80, U+F95B->U+62CF, U+F95C->U+6A02, U+F95D->U+8AFE, U+F95E->U+4E39, \
        U+F95F->U+5BE7, U+F960->U+6012, U+F961->U+7387, U+F962->U+7570, U+F963->U+5317, U+F964->U+78FB, U+F965->U+4FBF, U+F966->U+5FA9, \
        U+F967->U+4E0D, U+F968->U+6CCC, U+F969->U+6578, U+F96A->U+7D22, U+F96B->U+53C3, U+F96C->U+585E, U+F96D->U+7701, U+F96E->U+8449, \
        U+F96F->U+8AAA, U+F970->U+6BBA, U+F971->U+8FB0, U+F972->U+6C88, U+F973->U+62FE, U+F974->U+82E5, U+F975->U+63A0, U+F976->U+7565, \
        U+F977->U+4EAE, U+F978->U+5169, U+F979->U+51C9, U+F97A->U+6881, U+F97B->U+7CE7, U+F97C->U+826F, U+F97D->U+8AD2, U+F97E->U+91CF, \
        U+F97F->U+52F5, U+F980->U+5442, U+F981->U+5973, U+F982->U+5EEC, U+F983->U+65C5, U+F984->U+6FFE, U+F985->U+792A, U+F986->U+95AD, \
        U+F987->U+9A6A, U+F988->U+9E97, U+F989->U+9ECE, U+F98A->U+529B, U+F98B->U+66C6, U+F98C->U+6B77, U+F98D->U+8F62, U+F98E->U+5E74, \
        U+F98F->U+6190, U+F990->U+6200, U+F991->U+649A, U+F992->U+6F23, U+F993->U+7149, U+F994->U+7489, U+F995->U+79CA, U+F996->U+7DF4, \
        U+F997->U+806F, U+F998->U+8F26, U+F999->U+84EE, U+F99A->U+9023, U+F99B->U+934A, U+F99C->U+5217, U+F99D->U+52A3, U+F99E->U+54BD, \
        U+F99F->U+70C8, U+F9A0->U+88C2, U+F9A1->U+8AAA, U+F9A2->U+5EC9, U+F9A3->U+5FF5, U+F9A4->U+637B, U+F9A5->U+6BAE, U+F9A6->U+7C3E, \
        U+F9A7->U+7375, U+F9A8->U+4EE4, U+F9A9->U+56F9, U+F9AA->U+5BE7, U+F9AB->U+5DBA, U+F9AC->U+601C, U+F9AD->U+73B2, U+F9AE->U+7469, \
        U+F9AF->U+7F9A, U+F9B0->U+8046, U+F9B1->U+9234, U+F9B2->U+96F6, U+F9B3->U+9748, U+F9B4->U+9818, U+F9B5->U+4F8B, U+F9B6->U+79AE, \
        U+F9B7->U+91B4, U+F9B8->U+96B8, U+F9B9->U+60E1, U+F9BA->U+4E86, U+F9BB->U+50DA, U+F9BC->U+5BEE, U+F9BD->U+5C3F, U+F9BE->U+6599, \
        U+F9BF->U+6A02, U+F9C0->U+71CE, U+F9C1->U+7642, U+F9C2->U+84FC, U+F9C3->U+907C, U+F9C4->U+9F8D, U+F9C5->U+6688, U+F9C6->U+962E, \
        U+F9C7->U+5289, U+F9C8->U+677B, U+F9C9->U+67F3, U+F9CA->U+6D41, U+F9CB->U+6E9C, U+F9CC->U+7409, U+F9CD->U+7559, U+F9CE->U+786B, U+F9CF->U+7D10, \
        U+F9D0->U+985E, U+F9D1->U+516D, U+F9D2->U+622E, U+F9D3->U+9678, U+F9D4->U+502B, U+F9D5->U+5D19, U+F9D6->U+6DEA, U+F9D7->U+8F2A, U+F9D8->U+5F8B, \
        U+F9D9->U+6144, U+F9DA->U+6817, U+F9DB->U+7387, U+F9DC->U+9686, U+F9DD->U+5229, U+F9DE->U+540F, U+F9DF->U+5C65, U+F9E0->U+6613, U+F9E1->U+674E, \
        U+F9E2->U+68A8, U+F9E3->U+6CE5, U+F9E4->U+7406, U+F9E5->U+75E2, U+F9E6->U+7F79, U+F9E7->U+88CF, U+F9E8->U+88E1, U+F9E9->U+91CC, U+F9EA->U+96E2, \
        U+F9EB->U+533F, U+F9EC->U+6EBA, U+F9ED->U+541D, U+F9EE->U+71D0, U+F9EF->U+7498, U+F9F0->U+85FA, U+F9F1->U+96A3, U+F9F2->U+9C57, U+F9F3->U+9E9F, \
        U+F9F4->U+6797, U+F9F5->U+6DCB, U+F9F6->U+81E8, U+F9F7->U+7ACB, U+F9F8->U+7B20, U+F9F9->U+7C92, U+F9FA->U+72C0, U+F9FB->U+7099, U+F9FC->U+8B58, \
        U+F9FD->U+4EC0, U+F9FE->U+8336, U+F9FF->U+523A, U+FA00->U+5207, U+FA01->U+5EA6, U+FA02->U+62D3, U+FA03->U+7CD6, U+FA04->U+5B85, U+FA05->U+6D1E, \
        U+FA06->U+66B4, U+FA07->U+8F3B, U+FA08->U+884C, U+FA09->U+964D, U+FA0A->U+898B, U+FA0B->U+5ED3, U+FA0C->U+5140, U+FA0D->U+55C0, U+FA10->U+585A, \
        U+FA12->U+6674, U+FA15->U+51DE, U+FA16->U+732A, U+FA17->U+76CA, U+FA18->U+793C, U+FA19->U+795E, U+FA1A->U+7965, U+FA1B->U+798F, U+FA1C->U+9756, \
        U+FA1D->U+7CBE, U+FA1E->U+7FBD, U+FA20->U+8612, U+FA22->U+8AF8, U+FA25->U+9038, U+FA26->U+90FD, U+FA2A->U+98EF, U+FA2B->U+98FC, U+FA2C->U+9928, \
        U+FA2D->U+9DB4, U+FA30->U+4FAE, U+FA31->U+50E7, U+FA32->U+514D, U+FA33->U+52C9, U+FA34->U+52E4, U+FA35->U+5351, U+FA36->U+559D, U+FA37->U+5606, \
        U+FA38->U+5668, U+FA39->U+5840, U+FA3A->U+58A8, U+FA3B->U+5C64, U+FA3C->U+5C6E, U+FA3D->U+6094, U+FA3E->U+6168, U+FA3F->U+618E, U+FA40->U+61F2, \
        U+FA41->U+654F, U+FA42->U+65E2, U+FA43->U+6691, U+FA44->U+6885, U+FA45->U+6D77, U+FA46->U+6E1A, U+FA47->U+6F22, U+FA48->U+716E, U+FA49->U+722B, \
        U+FA4A->U+7422, U+FA4B->U+7891, U+FA4C->U+793E, U+FA4D->U+7949, U+FA4E->U+7948, U+FA4F->U+7950, U+FA50->U+7956, U+FA51->U+795D, U+FA52->U+798D, \
        U+FA53->U+798E, U+FA54->U+7A40, U+FA55->U+7A81, U+FA56->U+7BC0, U+FA57->U+7DF4, U+FA58->U+7E09, U+FA59->U+7E41, U+FA5A->U+7F72, U+FA5B->U+8005, \
        U+FA5C->U+81ED, U+FA5D->U+8279, U+FA5E->U+8279, U+FA5F->U+8457, U+FA60->U+8910, U+FA61->U+8996, U+FA62->U+8B01, U+FA63->U+8B39, U+FA64->U+8CD3, \
        U+FA65->U+8D08, U+FA66->U+8FB6, U+FA67->U+9038, U+FA68->U+96E3, U+FA69->U+97FF, U+FA6A->U+983B, U+FA70->U+4E26, U+FA71->U+51B5, U+FA72->U+5168, \
        U+FA73->U+4F80, U+FA74->U+5145, U+FA75->U+5180, U+FA76->U+52C7, U+FA77->U+52FA, U+FA78->U+559D, U+FA79->U+5555, U+FA7A->U+5599, U+FA7B->U+55E2, \
        U+FA7C->U+585A, U+FA7D->U+58B3, U+FA7E->U+5944, U+FA7F->U+5954, U+FA80->U+5A62, U+FA81->U+5B28, U+FA82->U+5ED2, U+FA83->U+5ED9, U+FA84->U+5F69, \
        U+FA85->U+5FAD, U+FA86->U+60D8, U+FA87->U+614E, U+FA88->U+6108, U+FA89->U+618E, U+FA8A->U+6160, U+FA8B->U+61F2, U+FA8C->U+6234, U+FA8D->U+63C4, \
        U+FA8E->U+641C, U+FA8F->U+6452, U+FA90->U+6556, U+FA91->U+6674, U+FA92->U+6717, U+FA93->U+671B, U+FA94->U+6756, U+FA95->U+6B79, U+FA96->U+6BBA, \
        U+FA97->U+6D41, U+FA98->U+6EDB, U+FA99->U+6ECB, U+FA9A->U+6F22, U+FA9B->U+701E, U+FA9C->U+716E, U+FA9D->U+77A7, U+FA9E->U+7235, U+FA9F->U+72AF, \
        U+FAA0->U+732A, U+FAA1->U+7471, U+FAA2->U+7506, U+FAA3->U+753B, U+FAA4->U+761D, U+FAA5->U+761F, U+FAA6->U+76CA, U+FAA7->U+76DB, U+FAA8->U+76F4, \
        U+FAA9->U+774A, U+FAAA->U+7740, U+FAAB->U+78CC, U+FAAC->U+7AB1, U+FAAD->U+7BC0, U+FAAE->U+7C7B, U+FAAF->U+7D5B, U+FAB0->U+7DF4, U+FAB1->U+7F3E, \
        U+FAB2->U+8005, U+FAB3->U+8352, U+FAB4->U+83EF, U+FAB5->U+8779, U+FAB6->U+8941, U+FAB7->U+8986, U+FAB8->U+8996, U+FAB9->U+8ABF, U+FABA->U+8AF8, \
        U+FABB->U+8ACB, U+FABC->U+8B01, U+FABD->U+8AFE, U+FABE->U+8AED, U+FABF->U+8B39, U+FAC0->U+8B8A, U+FAC1->U+8D08, U+FAC2->U+8F38, U+FAC3->U+9072, \
        U+FAC4->U+9199, U+FAC5->U+9276, U+FAC6->U+967C, U+FAC7->U+96E3, U+FAC8->U+9756, U+FAC9->U+97DB, U+FACA->U+97FF, U+FACB->U+980B, U+FACC->U+983B, \
        U+FACD->U+9B12, U+FACE->U+9F9C, U+FACF->U+2284A, U+FAD0->U+22844, U+FAD1->U+233D5, U+FAD2->U+3B9D, U+FAD3->U+4018, U+FAD4->U+4039, U+FAD5->U+25249, \
        U+FAD6->U+25CD0, U+FAD7->U+27ED3, U+FAD8->U+9F43, U+FAD9->U+9F8E, U+2F800->U+4E3D, U+2F801->U+4E38, U+2F802->U+4E41, U+2F803->U+20122, U+2F804->U+4F60, \
        U+2F805->U+4FAE, U+2F806->U+4FBB, U+2F807->U+5002, U+2F808->U+507A, U+2F809->U+5099, U+2F80A->U+50E7, U+2F80B->U+50CF, U+2F80C->U+349E, U+2F80D->U+2063A,\
        U+2F80E->U+514D, U+2F80F->U+5154, U+2F810->U+5164, U+2F811->U+5177, U+2F812->U+2051C, U+2F813->U+34B9, U+2F814->U+5167, U+2F815->U+518D, \
        U+2F816->U+2054B, U+2F817->U+5197, U+2F818->U+51A4, U+2F819->U+4ECC, U+2F81A->U+51AC, U+2F81B->U+51B5, U+2F81C->U+291DF, U+2F81D->U+51F5, \
        U+2F81E->U+5203, U+2F81F->U+34DF, U+2F820->U+523B, U+2F821->U+5246, U+2F822->U+5272, U+2F823->U+5277, U+2F824->U+3515, U+2F825->U+52C7, \
        U+2F826->U+52C9, U+2F827->U+52E4, U+2F828->U+52FA, U+2F829->U+5305, U+2F82A->U+5306, U+2F82B->U+5317, U+2F82C->U+5349, U+2F82D->U+5351, \
        U+2F82E->U+535A, U+2F82F->U+5373, U+2F830->U+537D, U+2F831->U+537F, U+2F832->U+537F, U+2F833->U+537F, U+2F834->U+20A2C, U+2F835->U+7070, \
        U+2F836->U+53CA, U+2F837->U+53DF, U+2F838->U+20B63, U+2F839->U+53EB, U+2F83A->U+53F1, U+2F83B->U+5406, U+2F83C->U+549E, U+2F83D->U+5438, \
        U+2F83E->U+5448, U+2F83F->U+5468, U+2F840->U+54A2, U+2F841->U+54F6, U+2F842->U+5510, U+2F843->U+5553, U+2F844->U+5563, U+2F845->U+5584, U+2F846->U+5584, \
        U+2F847->U+5599, U+2F848->U+55AB, U+2F849->U+55B3, U+2F84A->U+55C2, U+2F84B->U+5716, U+2F84C->U+5606, U+2F84D->U+5717, U+2F84E->U+5651, U+2F84F->U+5674, \
        U+2F850->U+5207, U+2F851->U+58EE, U+2F852->U+57CE, U+2F853->U+57F4, U+2F854->U+580D, U+2F855->U+578B, U+2F856->U+5832, U+2F857->U+5831, U+2F858->U+58AC, \
        U+2F859->U+214E4, U+2F85A->U+58F2, U+2F85B->U+58F7, U+2F85C->U+5906, U+2F85D->U+591A, U+2F85E->U+5922, U+2F85F->U+5962, U+2F860->U+216A8, U+2F861->U+216EA,\
        U+2F862->U+59EC, U+2F863->U+5A1B, U+2F864->U+5A27, U+2F865->U+59D8, U+2F866->U+5A66, U+2F867->U+36EE, U+2F868->U+36FC, U+2F869->U+5B08, U+2F86A->U+5B3E, \
        U+2F86B->U+5B3E, U+2F86C->U+219C8, U+2F86D->U+5BC3, U+2F86E->U+5BD8, U+2F86F->U+5BE7, U+2F870->U+5BF3, U+2F871->U+21B18, U+2F872->U+5BFF, U+2F873->U+5C06, \
        U+2F874->U+5F53, U+2F875->U+5C22, U+2F876->U+3781, U+2F877->U+5C60, U+2F878->U+5C6E, U+2F879->U+5CC0, U+2F87A->U+5C8D, U+2F87B->U+21DE4, U+2F87C->U+5D43, \
        U+2F87D->U+21DE6, U+2F87E->U+5D6E, U+2F87F->U+5D6B, U+2F880->U+5D7C, U+2F881->U+5DE1, U+2F882->U+5DE2, U+2F883->U+382F, U+2F884->U+5DFD, U+2F885->U+5E28, \
        U+2F886->U+5E3D, U+2F887->U+5E69, U+2F888->U+3862, U+2F889->U+22183, U+2F88A->U+387C, U+2F88B->U+5EB0, U+2F88C->U+5EB3, U+2F88D->U+5EB6, U+2F88E->U+5ECA, \
        U+2F88F->U+2A392, U+2F890->U+5EFE, U+2F891->U+22331, U+2F892->U+22331, U+2F893->U+8201, U+2F894->U+5F22, U+2F895->U+5F22, U+2F896->U+38C7, U+2F897->U+232B8, \
        U+2F898->U+261DA, U+2F899->U+5F62, U+2F89A->U+5F6B, U+2F89B->U+38E3, U+2F89C->U+5F9A, U+2F89D->U+5FCD, U+2F89E->U+5FD7, U+2F89F->U+5FF9, U+2F8A0->U+6081, \
        U+2F8A1->U+393A, U+2F8A2->U+391C, U+2F8A3->U+6094, U+2F8A4->U+226D4, U+2F8A5->U+60C7, U+2F8A6->U+6148, U+2F8A7->U+614C, U+2F8A8->U+614E, U+2F8A9->U+614C, \
        U+2F8AA->U+617A, U+2F8AB->U+618E, U+2F8AC->U+61B2, U+2F8AD->U+61A4, U+2F8AE->U+61AF, U+2F8AF->U+61DE, U+2F8B0->U+61F2, U+2F8B1->U+61F6, U+2F8B2->U+6210, \
        U+2F8B3->U+621B, U+2F8B4->U+625D, U+2F8B5->U+62B1, U+2F8B6->U+62D4, U+2F8B7->U+6350, U+2F8B8->U+22B0C, U+2F8B9->U+633D, U+2F8BA->U+62FC, U+2F8BB->U+6368, \
        U+2F8BC->U+6383, U+2F8BD->U+63E4, U+2F8BE->U+22BF1, U+2F8BF->U+6422, U+2F8C0->U+63C5, U+2F8C1->U+63A9, U+2F8C2->U+3A2E, U+2F8C3->U+6469, U+2F8C4->U+647E, \
        U+2F8C5->U+649D, U+2F8C6->U+6477, U+2F8C7->U+3A6C, U+2F8C8->U+654F, U+2F8C9->U+656C, U+2F8CA->U+2300A, U+2F8CB->U+65E3, U+2F8CC->U+66F8, U+2F8CD->U+6649, \
        U+2F8CE->U+3B19, U+2F8CF->U+6691, U+2F8D0->U+3B08, U+2F8D1->U+3AE4, U+2F8D2->U+5192, U+2F8D3->U+5195, U+2F8D4->U+6700, U+2F8D5->U+669C, U+2F8D6->U+80AD, \
        U+2F8D7->U+43D9, U+2F8D8->U+6717, U+2F8D9->U+671B, U+2F8DA->U+6721, U+2F8DB->U+675E, U+2F8DC->U+6753, U+2F8DD->U+233C3, U+2F8DE->U+3B49, U+2F8DF->U+67FA, \
        U+2F8E0->U+6785, U+2F8E1->U+6852, U+2F8E2->U+6885, U+2F8E3->U+2346D, U+2F8E4->U+688E, U+2F8E5->U+681F, U+2F8E6->U+6914, U+2F8E7->U+3B9D, U+2F8E8->U+6942, \
        U+2F8E9->U+69A3, U+2F8EA->U+69EA, U+2F8EB->U+6AA8, U+2F8EC->U+236A3, U+2F8ED->U+6ADB, U+2F8EE->U+3C18, U+2F8EF->U+6B21, U+2F8F0->U+238A7, U+2F8F1->U+6B54, \
        U+2F8F2->U+3C4E, U+2F8F3->U+6B72, U+2F8F4->U+6B9F, U+2F8F5->U+6BBA, U+2F8F6->U+6BBB, U+2F8F7->U+23A8D, U+2F8F8->U+21D0B, U+2F8F9->U+23AFA, U+2F8FA->U+6C4E, \
        U+2F8FB->U+23CBC, U+2F8FC->U+6CBF, U+2F8FD->U+6CCD, U+2F8FE->U+6C67, U+2F8FF->U+6D16, U+2F900->U+6D3E, U+2F901->U+6D77, U+2F902->U+6D41, U+2F903->U+6D69, \
        U+2F904->U+6D78, U+2F905->U+6D85, U+2F906->U+23D1E, U+2F907->U+6D34, U+2F908->U+6E2F, U+2F909->U+6E6E, U+2F90A->U+3D33, U+2F90B->U+6ECB, U+2F90C->U+6EC7, \
        U+2F90D->U+23ED1, U+2F90E->U+6DF9, U+2F90F->U+6F6E, U+2F910->U+23F5E, U+2F911->U+23F8E, U+2F912->U+6FC6, U+2F913->U+7039, U+2F914->U+701E, U+2F915->U+701B, \
        U+2F916->U+3D96, U+2F917->U+704A, U+2F918->U+707D, U+2F919->U+7077, U+2F91A->U+70AD, U+2F91B->U+20525, U+2F91C->U+7145, U+2F91D->U+24263, U+2F91E->U+719C, \
        U+2F91F->U+243AB, U+2F920->U+7228, U+2F921->U+7235, U+2F922->U+7250, U+2F923->U+24608, U+2F924->U+7280, U+2F925->U+7295, U+2F926->U+24735, U+2F927->U+24814, \
        U+2F928->U+737A, U+2F929->U+738B, U+2F92A->U+3EAC, U+2F92B->U+73A5, U+2F92C->U+3EB8, U+2F92D->U+3EB8, U+2F92E->U+7447, U+2F92F->U+745C, U+2F930->U+7471, \
        U+2F931->U+7485, U+2F932->U+74CA, U+2F933->U+3F1B, U+2F934->U+7524, U+2F935->U+24C36, U+2F936->U+753E, U+2F937->U+24C92, U+2F938->U+7570, U+2F939->U+2219F, \
        U+2F93A->U+7610, U+2F93B->U+24FA1, U+2F93C->U+24FB8, U+2F93D->U+25044, U+2F93E->U+3FFC, U+2F93F->U+4008, U+2F940->U+76F4, U+2F941->U+250F3, U+2F942->U+250F2, \
        U+2F943->U+25119, U+2F944->U+25133, U+2F945->U+771E, U+2F946->U+771F, U+2F947->U+771F, U+2F948->U+774A, U+2F949->U+4039, U+2F94A->U+778B, U+2F94B->U+4046, \
        U+2F94C->U+4096, U+2F94D->U+2541D, U+2F94E->U+784E, U+2F94F->U+788C, U+2F950->U+78CC, U+2F951->U+40E3, U+2F952->U+25626, U+2F953->U+7956, U+2F954->U+2569A, \
        U+2F955->U+256C5, U+2F956->U+798F, U+2F957->U+79EB, U+2F958->U+412F, U+2F959->U+7A40, U+2F95A->U+7A4A, U+2F95B->U+7A4F, U+2F95C->U+2597C, U+2F95D->U+25AA7, \
        U+2F95E->U+25AA7, U+2F95F->U+7AEE, U+2F960->U+4202, U+2F961->U+25BAB, U+2F962->U+7BC6, U+2F963->U+7BC9, U+2F964->U+4227, U+2F965->U+25C80, U+2F966->U+7CD2, \
        U+2F967->U+42A0, U+2F968->U+7CE8, U+2F969->U+7CE3, U+2F96A->U+7D00, U+2F96B->U+25F86, U+2F96C->U+7D63, U+2F96D->U+4301, U+2F96E->U+7DC7, U+2F96F->U+7E02, \
        U+2F970->U+7E45, U+2F971->U+4334, U+2F972->U+26228, U+2F973->U+26247, U+2F974->U+4359, U+2F975->U+262D9, U+2F976->U+7F7A, U+2F977->U+2633E, U+2F978->U+7F95, \
        U+2F979->U+7FFA, U+2F97A->U+8005, U+2F97B->U+264DA, U+2F97C->U+26523, U+2F97D->U+8060, U+2F97E->U+265A8, U+2F97F->U+8070, U+2F980->U+2335F, U+2F981->U+43D5, \
        U+2F982->U+80B2, U+2F983->U+8103, U+2F984->U+440B, U+2F985->U+813E, U+2F986->U+5AB5, U+2F987->U+267A7, U+2F988->U+267B5, U+2F989->U+23393, U+2F98A->U+2339C, \
        U+2F98B->U+8201, U+2F98C->U+8204, U+2F98D->U+8F9E, U+2F98E->U+446B, U+2F98F->U+8291, U+2F990->U+828B, U+2F991->U+829D, U+2F992->U+52B3, U+2F993->U+82B1, \
        U+2F994->U+82B3, U+2F995->U+82BD, U+2F996->U+82E6, U+2F997->U+26B3C, U+2F998->U+82E5, U+2F999->U+831D, U+2F99A->U+8363, U+2F99B->U+83AD, U+2F99C->U+8323, \
        U+2F99D->U+83BD, U+2F99E->U+83E7, U+2F99F->U+8457, U+2F9A0->U+8353, U+2F9A1->U+83CA, U+2F9A2->U+83CC, U+2F9A3->U+83DC, U+2F9A4->U+26C36, U+2F9A5->U+26D6B, \
        U+2F9A6->U+26CD5, U+2F9A7->U+452B, U+2F9A8->U+84F1, U+2F9A9->U+84F3, U+2F9AA->U+8516, U+2F9AB->U+273CA, U+2F9AC->U+8564, U+2F9AD->U+26F2C, U+2F9AE->U+455D, \
        U+2F9AF->U+4561, U+2F9B0->U+26FB1, U+2F9B1->U+270D2, U+2F9B2->U+456B, U+2F9B3->U+8650, U+2F9B4->U+865C, U+2F9B5->U+8667, U+2F9B6->U+8669, U+2F9B7->U+86A9, \
        U+2F9B8->U+8688, U+2F9B9->U+870E, U+2F9BA->U+86E2, U+2F9BB->U+8779, U+2F9BC->U+8728, U+2F9BD->U+876B, U+2F9BE->U+8786, U+2F9BF->U+45D7, U+2F9C0->U+87E1, \
        U+2F9C1->U+8801, U+2F9C2->U+45F9, U+2F9C3->U+8860, U+2F9C4->U+8863, U+2F9C5->U+27667, U+2F9C6->U+88D7, U+2F9C7->U+88DE, U+2F9C8->U+4635, U+2F9C9->U+88FA, \
        U+2F9CA->U+34BB, U+2F9CB->U+278AE, U+2F9CC->U+27966, U+2F9CD->U+46BE, U+2F9CE->U+46C7, U+2F9CF->U+8AA0, U+2F9D0->U+8AED, U+2F9D1->U+8B8A, U+2F9D2->U+8C55, \
        U+2F9D3->U+27CA8, U+2F9D4->U+8CAB, U+2F9D5->U+8CC1, U+2F9D6->U+8D1B, U+2F9D7->U+8D77, U+2F9D8->U+27F2F, U+2F9D9->U+20804, U+2F9DA->U+8DCB, U+2F9DB->U+8DBC, \
        U+2F9DC->U+8DF0, U+2F9DD->U+208DE, U+2F9DE->U+8ED4, U+2F9DF->U+8F38, U+2F9E0->U+285D2, U+2F9E1->U+285ED, U+2F9E2->U+9094, U+2F9E3->U+90F1, U+2F9E4->U+9111, \
        U+2F9E5->U+2872E, U+2F9E6->U+911B, U+2F9E7->U+9238, U+2F9E8->U+92D7, U+2F9E9->U+92D8, U+2F9EA->U+927C, U+2F9EB->U+93F9, U+2F9EC->U+9415, U+2F9ED->U+28BFA, \
        U+2F9EE->U+958B, U+2F9EF->U+4995, U+2F9F0->U+95B7, U+2F9F1->U+28D77, U+2F9F2->U+49E6, U+2F9F3->U+96C3, U+2F9F4->U+5DB2, U+2F9F5->U+9723, U+2F9F6->U+29145, \
        U+2F9F7->U+2921A, U+2F9F8->U+4A6E, U+2F9F9->U+4A76, U+2F9FA->U+97E0, U+2F9FB->U+2940A, U+2F9FC->U+4AB2, U+2F9FD->U+29496, U+2F9FE->U+980B, U+2F9FF->U+980B, \
        U+2FA00->U+9829, U+2FA01->U+295B6, U+2FA02->U+98E2, U+2FA03->U+4B33, U+2FA04->U+9929, U+2FA05->U+99A7, U+2FA06->U+99C2, U+2FA07->U+99FE, U+2FA08->U+4BCE, \
        U+2FA09->U+29B30, U+2FA0A->U+9B12, U+2FA0B->U+9C40, U+2FA0C->U+9CFD, U+2FA0D->U+4CCE, U+2FA0E->U+4CED, U+2FA0F->U+9D67, U+2FA10->U+2A0CE, U+2FA11->U+4CF8, \
        U+2FA12->U+2A105, U+2FA13->U+2A20E, U+2FA14->U+2A291, U+2FA15->U+9EBB, U+2FA16->U+4D56, U+2FA17->U+9EF9, U+2FA18->U+9EFE, U+2FA19->U+9F05, U+2FA1A->U+9F0F, \
        U+2FA1B->U+9F16, U+2FA1C->U+9F3B, U+2FA1D->U+2A600, U+2F00->U+4E00, U+2F01->U+4E28, U+2F02->U+4E36, U+2F03->U+4E3F, U+2F04->U+4E59, U+2F05->U+4E85, \
        U+2F06->U+4E8C, U+2F07->U+4EA0, U+2F08->U+4EBA, U+2F09->U+513F, U+2F0A->U+5165, U+2F0B->U+516B, U+2F0C->U+5182, U+2F0D->U+5196, U+2F0E->U+51AB, \
        U+2F0F->U+51E0, U+2F10->U+51F5, U+2F11->U+5200, U+2F12->U+529B, U+2F13->U+52F9, U+2F14->U+5315, U+2F15->U+531A, U+2F16->U+5338, U+2F17->U+5341, \
        U+2F18->U+535C, U+2F19->U+5369, U+2F1A->U+5382, U+2F1B->U+53B6, U+2F1C->U+53C8, U+2F1D->U+53E3, U+2F1E->U+56D7, U+2F1F->U+571F, U+2F20->U+58EB, \
        U+2F21->U+5902, U+2F22->U+590A, U+2F23->U+5915, U+2F24->U+5927, U+2F25->U+5973, U+2F26->U+5B50, U+2F27->U+5B80, U+2F28->U+5BF8, U+2F29->U+5C0F, \
        U+2F2A->U+5C22, U+2F2B->U+5C38, U+2F2C->U+5C6E, U+2F2D->U+5C71, U+2F2E->U+5DDB, U+2F2F->U+5DE5, U+2F30->U+5DF1, U+2F31->U+5DFE, U+2F32->U+5E72, \
        U+2F33->U+5E7A, U+2F34->U+5E7F, U+2F35->U+5EF4, U+2F36->U+5EFE, U+2F37->U+5F0B, U+2F38->U+5F13, U+2F39->U+5F50, U+2F3A->U+5F61, U+2F3B->U+5F73, \
        U+2F3C->U+5FC3, U+2F3D->U+6208, U+2F3E->U+6236, U+2F3F->U+624B, U+2F40->U+652F, U+2F41->U+6534, U+2F42->U+6587, U+2F43->U+6597, U+2F44->U+65A4, \
        U+2F45->U+65B9, U+2F46->U+65E0, U+2F47->U+65E5, U+2F48->U+66F0, U+2F49->U+6708, U+2F4A->U+6728, U+2F4B->U+6B20, U+2F4C->U+6B62, U+2F4D->U+6B79, \
        U+2F4E->U+6BB3, U+2F4F->U+6BCB, U+2F50->U+6BD4, U+2F51->U+6BDB, U+2F52->U+6C0F, U+2F53->U+6C14, U+2F54->U+6C34, U+2F55->U+706B, U+2F56->U+722A, \
        U+2F57->U+7236, U+2F58->U+723B, U+2F59->U+723F, U+2F5A->U+7247, U+2F5B->U+7259, U+2F5C->U+725B, U+2F5D->U+72AC, U+2F5E->U+7384, U+2F5F->U+7389, \
        U+2F60->U+74DC, U+2F61->U+74E6, U+2F62->U+7518, U+2F63->U+751F, U+2F64->U+7528, U+2F65->U+7530, U+2F66->U+758B, U+2F67->U+7592, U+2F68->U+7676, \
        U+2F69->U+767D, U+2F6A->U+76AE, U+2F6B->U+76BF, U+2F6C->U+76EE, U+2F6D->U+77DB, U+2F6E->U+77E2, U+2F6F->U+77F3, U+2F70->U+793A, U+2F71->U+79B8, \
        U+2F72->U+79BE, U+2F73->U+7A74, U+2F74->U+7ACB, U+2F75->U+7AF9, U+2F76->U+7C73, U+2F77->U+7CF8, U+2F78->U+7F36, U+2F79->U+7F51, U+2F7A->U+7F8A, \
        U+2F7B->U+7FBD, U+2F7C->U+8001, U+2F7D->U+800C, U+2F7E->U+8012, U+2F7F->U+8033, U+2F80->U+807F, U+2F81->U+8089, U+2F82->U+81E3, U+2F83->U+81EA, \
        U+2F84->U+81F3, U+2F85->U+81FC, U+2F86->U+820C, U+2F87->U+821B, U+2F88->U+821F, U+2F89->U+826E, U+2F8A->U+8272, U+2F8B->U+8278, U+2F8C->U+864D, \
        U+2F8D->U+866B, U+2F8E->U+8840, U+2F8F->U+884C, U+2F90->U+8863, U+2F91->U+897E, U+2F92->U+898B, U+2F93->U+89D2, U+2F94->U+8A00, U+2F95->U+8C37, \
        U+2F96->U+8C46, U+2F97->U+8C55, U+2F98->U+8C78, U+2F99->U+8C9D, U+2F9A->U+8D64, U+2F9B->U+8D70, U+2F9C->U+8DB3, U+2F9D->U+8EAB, U+2F9E->U+8ECA, \
        U+2F9F->U+8F9B, U+2FA0->U+8FB0, U+2FA1->U+8FB5, U+2FA2->U+9091, U+2FA3->U+9149, U+2FA4->U+91C6, U+2FA5->U+91CC, U+2FA6->U+91D1, U+2FA7->U+9577, \
        U+2FA8->U+9580, U+2FA9->U+961C, U+2FAA->U+96B6, U+2FAB->U+96B9, U+2FAC->U+96E8, U+2FAD->U+9751, U+2FAE->U+975E, U+2FAF->U+9762, U+2FB0->U+9769, \
        U+2FB1->U+97CB, U+2FB2->U+97ED, U+2FB3->U+97F3, U+2FB4->U+9801, U+2FB5->U+98A8, U+2FB6->U+98DB, U+2FB7->U+98DF, U+2FB8->U+9996, U+2FB9->U+9999, \
        U+2FBA->U+99AC, U+2FBB->U+9AA8, U+2FBC->U+9AD8, U+2FBD->U+9ADF, U+2FBE->U+9B25, U+2FBF->U+9B2F, U+2FC0->U+9B32, U+2FC1->U+9B3C, U+2FC2->U+9B5A, \
        U+2FC3->U+9CE5, U+2FC4->U+9E75, U+2FC5->U+9E7F, U+2FC6->U+9EA5, U+2FC7->U+9EBB, U+2FC8->U+9EC3, U+2FC9->U+9ECD, U+2FCA->U+9ED1, U+2FCB->U+9EF9, \
        U+2FCC->U+9EFD, U+2FCD->U+9F0E, U+2FCE->U+9F13, U+2FCF->U+9F20, U+2FD0->U+9F3B, U+2FD1->U+9F4A, U+2FD2->U+9F52, U+2FD3->U+9F8D, U+2FD4->U+9F9C, \
        U+2FD5->U+9FA0, U+3042->U+3041, U+3044->U+3043, U+3046->U+3045, U+3048->U+3047, U+304A->U+3049, U+304C->U+304B, U+304E->U+304D, U+3050->U+304F, \
        U+3052->U+3051, U+3054->U+3053, U+3056->U+3055, U+3058->U+3057, U+305A->U+3059, U+305C->U+305B, U+305E->U+305D, U+3060->U+305F, U+3062->U+3061, \
        U+3064->U+3063, U+3065->U+3063, U+3067->U+3066, U+3069->U+3068, U+3070->U+306F, U+3071->U+306F, U+3073->U+3072, U+3074->U+3072, U+3076->U+3075, \
        U+3077->U+3075, U+3079->U+3078, U+307A->U+3078, U+307C->U+307B, U+307D->U+307B, U+3084->U+3083, U+3086->U+3085, U+3088->U+3087, U+308F->U+308E, \
        U+3094->U+3046, U+3095->U+304B, U+3096->U+3051, U+30A2->U+30A1, U+30A4->U+30A3, U+30A6->U+30A5, U+30A8->U+30A7, U+30AA->U+30A9, U+30AC->U+30AB, \
        U+30AE->U+30AD, U+30B0->U+30AF, U+30B2->U+30B1, U+30B4->U+30B3, U+30B6->U+30B5, U+30B8->U+30B7, U+30BA->U+30B9, U+30BC->U+30BB, U+30BE->U+30BD, \
        U+30C0->U+30BF, U+30C2->U+30C1, U+30C5->U+30C4, U+30C7->U+30C6, U+30C9->U+30C8, U+30D0->U+30CF, U+30D1->U+30CF, U+30D3->U+30D2, U+30D4->U+30D2, \
        U+30D6->U+30D5, U+30D7->U+30D5, U+30D9->U+30D8, U+30DA->U+30D8, U+30DC->U+30DB, U+30DD->U+30DB, U+30E4->U+30E3, U+30E6->U+30E5, U+30E8->U+30E7, \
        U+30EF->U+30EE, U+30F4->U+30A6, U+30AB->U+30F5, U+30B1->U+30F6, U+30F7->U+30EF, U+30F8->U+30F0, U+30F9->U+30F1, U+30FA->U+30F2, U+30AF->U+31F0, \
        U+30B7->U+31F1, U+30B9->U+31F2, U+30C8->U+31F3, U+30CC->U+31F4, U+30CF->U+31F5, U+30D2->U+31F6, U+30D5->U+31F7, U+30D8->U+31F8, U+30DB->U+31F9, \
        U+30E0->U+31FA, U+30E9->U+31FB, U+30EA->U+31FC, U+30EB->U+31FD, U+30EC->U+31FE, U+30ED->U+31FF, U+FF66->U+30F2, U+FF67->U+30A1, U+FF68->U+30A3, \
        U+FF69->U+30A5, U+FF6A->U+30A7, U+FF6B->U+30A9, U+FF6C->U+30E3, U+FF6D->U+30E5, U+FF6E->U+30E7, U+FF6F->U+30C3, U+FF71->U+30A1, U+FF72->U+30A3, \
        U+FF73->U+30A5, U+FF74->U+30A7, U+FF75->U+30A9, U+FF76->U+30AB, U+FF77->U+30AD, U+FF78->U+30AF, U+FF79->U+30B1, U+FF7A->U+30B3, U+FF7B->U+30B5, \
        U+FF7C->U+30B7, U+FF7D->U+30B9, U+FF7E->U+30BB, U+FF7F->U+30BD, U+FF80->U+30BF, U+FF81->U+30C1, U+FF82->U+30C3, U+FF83->U+30C6, U+FF84->U+30C8, \
        U+FF85->U+30CA, U+FF86->U+30CB, U+FF87->U+30CC, U+FF88->U+30CD, U+FF89->U+30CE, U+FF8A->U+30CF, U+FF8B->U+30D2, U+FF8C->U+30D5, U+FF8D->U+30D8, \
        U+FF8E->U+30DB, U+FF8F->U+30DE, U+FF90->U+30DF, U+FF91->U+30E0, U+FF92->U+30E1, U+FF93->U+30E2, U+FF94->U+30E3, U+FF95->U+30E5, U+FF96->U+30E7, \
        U+FF97->U+30E9, U+FF98->U+30EA, U+FF99->U+30EB, U+FF9A->U+30EC, U+FF9B->U+30ED, U+FF9C->U+30EF, U+FF9D->U+30F3, U+FFA0->U+3164, U+FFA1->U+3131, \
        U+FFA2->U+3132, U+FFA3->U+3133, U+FFA4->U+3134, U+FFA5->U+3135, U+FFA6->U+3136, U+FFA7->U+3137, U+FFA8->U+3138, U+FFA9->U+3139, U+FFAA->U+313A, \
        U+FFAB->U+313B, U+FFAC->U+313C, U+FFAD->U+313D, U+FFAE->U+313E, U+FFAF->U+313F, U+FFB0->U+3140, U+FFB1->U+3141, U+FFB2->U+3142, U+FFB3->U+3143, \
        U+FFB4->U+3144, U+FFB5->U+3145, U+FFB6->U+3146, U+FFB7->U+3147, U+FFB8->U+3148, U+FFB9->U+3149, U+FFBA->U+314A, U+FFBB->U+314B, U+FFBC->U+314C, \
        U+FFBD->U+314D, U+FFBE->U+314E, U+FFC2->U+314F, U+FFC3->U+3150, U+FFC4->U+3151, U+FFC5->U+3152, U+FFC6->U+3153, U+FFC7->U+3154, U+FFCA->U+3155, \
        U+FFCB->U+3156, U+FFCC->U+3157, U+FFCD->U+3158, U+FFCE->U+3159, U+FFCF->U+315A, U+FFD2->U+315B, U+FFD3->U+315C, U+FFD4->U+315D, U+FFD5->U+315E, \
        U+FFD6->U+315F, U+FFD7->U+3160, U+FFDA->U+3161, U+FFDB->U+3162, U+FFDC->U+3163, U+3131->U+1100, U+3132->U+1101, U+3133->U+11AA, U+3134->U+1102, \
        U+3135->U+11AC, U+3136->U+11AD, U+3137->U+1103, U+3138->U+1104, U+3139->U+1105, U+313A->U+11B0, U+313B->U+11B1, U+313C->U+11B2, U+313D->U+11B3, \
        U+313E->U+11B4, U+313F->U+11B5, U+3140->U+111A, U+3141->U+1106, U+3142->U+1107, U+3143->U+1108, U+3144->U+1121, U+3145->U+1109, U+3146->U+110A, \
        U+3147->U+110B, U+3148->U+110C, U+3149->U+110D, U+314A->U+110E, U+314B->U+110F, U+314C->U+1110, U+314D->U+1111, U+314E->U+1112, U+314F->U+1161, \
        U+3150->U+1162, U+3151->U+1163, U+3152->U+1164, U+3153->U+1165, U+3154->U+1166, U+3155->U+1167, U+3156->U+1168, U+3157->U+1169, U+3158->U+116A, \
        U+3159->U+116B, U+315A->U+116C, U+315B->U+116D, U+315C->U+116E, U+315D->U+116F, U+315E->U+1170, U+315F->U+1171, U+3160->U+1172, U+3161->U+1173, \
        U+3162->U+1174, U+3163->U+1175, U+3165->U+1114, U+3166->U+1115, U+3167->U+11C7, U+3168->U+11C8, U+3169->U+11CC, U+316A->U+11CE, U+316B->U+11D3, \
        U+316C->U+11D7, U+316D->U+11D9, U+316E->U+111C, U+316F->U+11DD, U+3170->U+11DF, U+3171->U+111D, U+3172->U+111E, U+3173->U+1120, U+3174->U+1122, \
        U+3175->U+1123, U+3176->U+1127, U+3177->U+1129, U+3178->U+112B, U+3179->U+112C, U+317A->U+112D, U+317B->U+112E, U+317C->U+112F, U+317D->U+1132, \
        U+317E->U+1136, U+317F->U+1140, U+3180->U+1147, U+3181->U+114C, U+3182->U+11F1, U+3183->U+11F2, U+3184->U+1157, U+3185->U+1158, U+3186->U+1159, \
        U+3187->U+1184, U+3188->U+1185, U+3189->U+1188, U+318A->U+1191, U+318B->U+1192, U+318C->U+1194, U+318D->U+119E, U+318E->U+11A1, U+A490->U+A408, \
        U+A491->U+A1B9, U+4E00..U+9FBB, U+3400..U+4DB5, U+20000..U+2A6D6, U+FA0E, U+FA0F, U+FA11, U+FA13, U+FA14, U+FA1F, U+FA21, U+FA23, U+FA24, U+FA27, \
        U+FA28, U+FA29, U+3105..U+312C, U+31A0..U+31B7, U+3041, U+3043, U+3045, U+3047, U+3049, U+304B, U+304D, U+304F, U+3051, U+3053, U+3055, U+3057, \
        U+3059, U+305B, U+305D, U+305F, U+3061, U+3063, U+3066, U+3068, U+306A..U+306F, U+3072, U+3075, U+3078, U+307B, U+307E..U+3083, U+3085, U+3087, \
        U+3089..U+308E, U+3090..U+3093, U+30A1, U+30A3, U+30A5, U+30A7, U+30A9, U+30AD, U+30AF, U+30B3, U+30B5, U+30BB, U+30BD, U+30BF, U+30C1, U+30C3, \
        U+30C4, U+30C6, U+30CA, U+30CB, U+30CD, U+30CE, U+30DE, U+30DF, U+30E1, U+30E2, U+30E3, U+30E5, U+30E7, U+30EE, U+30F0..U+30F3, U+30F5, U+30F6, \
        U+31F0, U+31F1, U+31F2, U+31F3, U+31F4, U+31F5, U+31F6, U+31F7, U+31F8, U+31F9, U+31FA, U+31FB, U+31FC, U+31FD, U+31FE, U+31FF, U+AC00..U+D7A3, \
        U+1100..U+1159, U+1161..U+11A2, U+11A8..U+11F9, U+A000..U+A48C, U+A492..U+A4C6
    ngram_chars = U+4E00..U+9FBB, U+3400..U+4DB5, U+20000..U+2A6D6, U+FA0E, U+FA0F, U+FA11, U+FA13, U+FA14, U+FA1F, U+FA21, U+FA23, U+FA24, U+FA27, U+FA28, \
        U+FA29, U+3105..U+312C, U+31A0..U+31B7, U+3041, U+3043, U+3045, U+3047, U+3049, U+304B, U+304D, U+304F, U+3051, U+3053, U+3055, U+3057, U+3059, U+305B, \
        U+305D, U+305F, U+3061, U+3063, U+3066, U+3068, U+306A..U+306F, U+3072, U+3075, U+3078, U+307B, U+307E..U+3083, U+3085, U+3087, U+3089..U+308E, \
        U+3090..U+3093, U+30A1, U+30A3, U+30A5, U+30A7, U+30A9, U+30AD, U+30AF, U+30B3, U+30B5, U+30BB, U+30BD, U+30BF, U+30C1, U+30C3, U+30C4, U+30C6, \
        U+30CA, U+30CB, U+30CD, U+30CE, U+30DE, U+30DF, U+30E1, U+30E2, U+30E3, U+30E5, U+30E7, U+30EE, U+30F0..U+30F3, U+30F5, U+30F6, U+31F0, U+31F1, \
        U+31F2, U+31F3, U+31F4, U+31F5, U+31F6, U+31F7, U+31F8, U+31F9, U+31FA, U+31FB, U+31FC, U+31FD, U+31FE, U+31FF, U+AC00..U+D7A3, U+1100..U+1159, \
        U+1161..U+11A2, U+11A8..U+11F9, U+A000..U+A48C, U+A492..U+A4C6
    ngram_len = 1
}

''')

    #剩余的index
    for no in range(2,len(table_id)+1):
        conf.write("index " + table_id[no] + " : " + table_id[1] + "\n{\n")
        conf.write("    source = " + table_id[no] + "\n")
        conf.write("    path = " + SPHINX + "/data/" + table_id[no] + "\n}\n\n")
    #全局index定义
    conf.write("indexer\n{\n    mem_limit = " + MEM_LIMIT + "\n}\n\n")
    #searched服务定义
    conf.write('''\
searchd
{
    listen = 9312
    read_timeout = 5
    max_children = 1000
    seamless_rotate = 1
    preopen_indexes = 1
    unlink_old = 1
    pid_file = ''' + SPHINX + '''/log/searchd_mysql.pid
    log = ''' + SPHINX + '''/log/searchd_mysql.log
    query_log = ''' + SPHINX + '''/log/query_mysql.log
    binlog_path =
}''')

cur.close()
conn.close()

#结束searchd服务
os.system(SPHINX + r"/bin/searchd --config " + SPHINX + r"/mysql.conf --stop")
#添加索引
command = SPHINX + r"/bin/indexer --config " + SPHINX + r"/mysql.conf"
for no in range(old_table_len+1 , len(table_id)+1):
    command += " "
    command += table_id[no]
os.system(command)
time.sleep(3)
#建立索引
os.system(SPHINX + r"/bin/searchd --config " + SPHINX + r"/mysql.conf")

#保存table_id字典
with open(SPHINX + "/mysql.pickle","wb") as pic:
    pickle.dump(table_id,pic)

#写PHP文件
with open(PHP + r"/index.php","w",encoding="utf-8") as php:
    php.write(r'''<?php
	error_reporting(0);	//关闭错误提示
	require ( "sphinxapi.php" );	//spinix搜索引擎
	
	$num = 0;	//本页的条目
	$rets = null;	//用于保存返回最多PAGE_NUM个结果集
	$page = 0;	//从某处开始检索
	$quest = strip_tags(trim($_GET['quest']));
	$md5 = strip_tags(trim($_GET['md5']));
	$full = strip_tags(trim($_GET['full']));
	
	const SERVER_PORT = 9312;	//Sphinx服务端口
	const CONNECT_TIMEOUT = 30;	//连接超时设置
	const PAGE_NUM = 10;	//单页最大显示数目
	const MAX_NUM = 200;	//需与 csft.conf 设置的最大返回结果数相同
	const DATABASE = "mydata";	//数据库库名
	const USERNAME = "root";	//数据库用户名
	const PASSWORD = "''' + PASSWD + r'''";	//数据库密码
	
	//定义 table_id 对应的表名
''')
    for no in range(1,len(table_id)+1):
        php.write("\t$table[\"" + str(no) + "\"] = \"" + table_id[no] + "\";\n")
        
    php.write("\t//定义索引表名\n")
    for no in range(1,len(table_id)+1):
        php.write("\t$index[\"" + str(no) + "\"] = \"" + FIRST_COLUMN[table_id[no]] + "\";\n")

    php.write(r'''    if(isset($_GET['quest']))	//如果搜索了条目
	{
		if($_GET['md5']==1)	//16位md5
		{
			$quest=substr(md5($quest),8,16);
		}
		if($_GET['md5']==2)	//32位md5
		{
			$quest=md5($quest);
		}
		$cl = new SphinxClient();
		// 返回结果设置
		$opts = array
		(
			"before_match"		=> "<font color=red>",
			"after_match"		=> "</font>",
			"chunk_separator"	=> " ... ",
			"limit"				=> 256,
			"around"			=> 5,
		);
		$cl->SetServer ('127.0.0.1', SERVER_PORT);
		$cl->SetConnectTimeout ( CONNECT_TIMEOUT );
		$cl->SetArrayResult ( true );
		// 设置是否全文匹配
		if(isset($_GET['full']) && $_GET['full'] == 1)
		{
			$cl->SetMatchMode(SPH_MATCH_ALL);
		}
		else
		{
			$cl->SetMatchMode(SPH_MATCH_ANY);
		}
		//设置检索位置
		if(isset($_GET['page']))
		{
			$page = intval(trim($_GET['page'])) > 0 ? intval(trim($_GET['page']))-1 : 0;
			$page = $page * PAGE_NUM;
		}
		
		$cl->setLimits($page,PAGE_NUM,MAX_NUM);
		$res = $cl->query ( ".{$quest}.", "*" );
		
		mysql_connect("localhost",USERNAME,PASSWORD); 
		mysql_select_db(DATABASE);	
		
		if ( is_array($res["matches"]) )
		{
			mysql_query("set names utf8");
			for (; $num < count($res["matches"]) ; $num++ )
			{
				$uid = $res["matches"][$num]["id"];	//取得第一列数据
				$table_id = $res["matches"][$num]["attrs"]["table_id"];	//取得table_id
				$table_name = $table[$table_id];
				$sql = "SELECT * FROM {$table_name} WHERE {$index[$table_id]} = {$uid}";
				$rets[$num] = mysql_query($sql);
			}
		}
	}
?>

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="zh-CN">
<head>
<title>The Web of Answers</title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<link rel="stylesheet" type="text/css" href="html/default.css" />
	<style type="text/css">
		body,td,th 
		{
			color: #FFF;
		}
		a:link 
		{
			color: #0C0;
			text-decoration: none;
		}
		body 
		{
			background-color: #000;
		}
		a:visited 
		{
			text-decoration: none;
			color: #999;
		}
		a:hover 
		{
			text-decoration: none;
		}
		a:active 
		{
			text-decoration: none;
			color: #F00;
		}
		.pages
		{
			clear: both;
			text-align: right;
			padding: 8px 0;
		}
		.pages a
		{
			display: inline-block;
			height: 20px;
			line-height: 20px;
			border: 1px solid #228B22;
			padding: 0 8px;
			color: #228B22;
			margin: 5px 2px;
			background: #2F2F2F;
		}
		.pages a:hover
		{
			background: #228B22;
			color: white;
		}
		.pages span 
		{
			display: inline-block;
			height: 20px;
			line-height: 20px;
			border: 1px solid #228B22;
			padding: 0 8px;
			margin: 5px 2px;
			background: #228B22; /*#228B22;*/
			color: white;	
		}
		#create_form label
		{
			margin-left: 10px;
		}
		#create_form em
		{
			margin-left: 60px;
		}
    </style>
<script>
<!--
	function check(form)
	{
		if(form.quest.value=="")
		{
			alert("不能为空值！");
			form.quest.focus();
			return false;
		}
	}
-->
</script>
</head>

<body>
	<div id="container">
		<div id="header"><h1>The Web of Answers</h1></div><br /><br />
		
		<div id="content">
			<form name="form" method="GET">
				<div id="create_form">
					<p><em></em>
						<label for=""><input type="checkbox" name="full" value="1" <?php echo !empty($_GET['full'])?'checked':'';?> />完整匹配</label>
						<label></label>
						<label for=""><input type="checkbox" name="md5" value="1" <?php echo !empty($_GET['md5'])?'checked':'';?> />MD5匹配</label>
					</p>
					<p style="text-align:center;margin:0 auto;">
						<label><input class="inurl" size="26" id="unurl" name="quest" value="<?php echo strip_tags(trim($_GET['quest']));?>" /></label>
						<span class="but"><input onclick="check(form)" type="submit" value="Search" class="submit" /></span>
					</p>
				</div>
			</form>
			
			<?php	
				if ($num > 0)	//找到了结果
				{
					echo "<br/>找到与&nbsp{$quest}&nbsp相关的结果 {$res[total_found]} 个。用时 {$res[time]} 秒。<ol start=\"" . (string)($page+1) . "\">";
					for ($no = 0 ; $no < $num ; $no++)	//显示结果
					{
						$row = mysql_fetch_assoc($rets[$no]);	//取得单行数据
						$keys = array_keys($row);	//取得列名
						$table_id = $res["matches"][$no]["attrs"]["table_id"];
						$table_name = $table[$table_id];	//取得表名
						$retContent = $cl->buildExcerpts($row,$table_name,$quest,$opts);	//取得高亮关键字后的数据
						echo "<li><font color=#00CD00>Table&nbsp;:&nbsp;{$table_name}</font><br /><br />";
						//输出信息
						for ($i = 0 ; $i < count($row) ; $i++)
						{
							$column_name = $keys[$i];	//取得本条列名
							if ($column_name == $index[$res["matches"][$no]["attrs"]["table_id"]])	//不输出行数
								continue;
							if (empty($retContent[$i]))	//不输出空白数据
								continue;
							echo $column_name;	//输出列名
							echo "&nbsp;:&nbsp;";
							echo $retContent[$i];	//输出高亮关键字后的数据
							echo "<br />";
						}
						echo '<br /></li>';
					}
					echo '</ol>';
				} 
				elseif (isset($_GET['quest']))
				{
					echo "<br/>找不到与&nbsp{$quest}&nbsp相关的结果。请更换其他关键词试试。";				
				}
			?>
			
			<div class="pages">
				<?php
					if($num != 0)
					{
						//取得页面数
						$pagecount = (int)($res[total_found] / PAGE_NUM);
						if(($res[total_found] % PAGE_NUM)!=0)	//找到的条目不足两页
						{
							$pagecount = $pagecount + 1;
						}
						if($pagecount > MAX_NUM/PAGE_NUM)	//显示的条目不超过限制
						{
							$pagecount = MAX_NUM/PAGE_NUM;
						}
						//设置高亮页数
						$highlightid = intval(trim($_GET['page']))>1 ? intval(trim($_GET['page'])) : 1;
						//设置页面按钮
						for ($pageno=1; $pageno <= $pagecount; $pageno++) 
						{ 
							if($highlightid==$pageno)
							{
								echo "<span>{$pageno}</span>";
							}
							else
							{
								echo "<a href=\"?quest={$quest}&page={$pageno}&md5={$md5}&full={$full}\">{$pageno}</a>";
							}
						}
					}
				?>
			</div>
		</div>
	</div>
</body>
</html>''')