========Magia_FP_Toolbar_v1.0 使用说明===========

1.请先使用Fullprof_suite制作正确的pcr。

2.保证pcr位于全英文路径下，且pcr中的各项路径（dat路径、仪器路径）不含中文字符。

3.确保pcr中各个原子的名称不重名。（例如，有多个Cl6i时，需重名为Cl6i_1,Cl6i_2等）

4.如需采用该程序精修择优与不对称型参数，请先手动修改pcr中相关代码（AsyLim，Pr1 Pr2 Pr3等）。

5.先使用参数库生成，生成参数库文件（.JSON），然后使用步骤生成，生成步骤文件（.JSON），最后使用精修主控进行精修。

6.精修主控会自动搜索fp2k.exe文件，若未找到则需要手动指定。


===========参数库生成===============

可自动读取XRD与TOF，自动识别手动插入背底数目，自动识别编码格式并自动转换为UTF-8编码，自动检测是否存在“! Current global Chi2 (Bragg contrib.) = ”，不存在则自动生成。可更改字体大小。

###无法读取各向异性B值###


========步骤生成============

友好的GUI界面，允许用户批量设置步长，以及手动修改value值，允许Step步骤批量选中，进行复制与删除操作，允许外部导入参数库，具有一键全选/一键取消功能。

###新步骤仅能添加在末尾，不能在中间加入新的步骤，且不同Step之间无法互换位置###


==========精修主控============

自动搜索fp2k.exe执行文件，且允许用户手动指定。自动识别精修目录下.pcr与.dat文件（多个文件则需要手动滚轮选择）。主日志界面每100ms刷新，且仅保留最新100行数据，以提升性能。可暂停，但需等待当前Step结束后生效。自动检测精修中各类报错以及未收敛现象，记录并输出。


===================================

!!!注意：该程序完全免费，仅供学习与交流使用，禁止用于任何商业用途!!!

若有任何问题或建议，请联系开发者。

Yujun Wan, PKUSZ Xiao Lab. wan_yujun@stu.pku.edu.cn
