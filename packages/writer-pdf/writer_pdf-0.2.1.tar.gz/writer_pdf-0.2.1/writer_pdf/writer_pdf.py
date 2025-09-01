# encoding: utf-8
# @File  : pdf_writer1_0.py
# @Author: ronin.G
# @Date  : 2025/08/21/14:44
import base64
import hashlib
import excel2img
import pymysql
import time
import re
import datetime
import os
import traceback
import json
import requests
import ssl
import smtplib
from tableauserverclient import Server, TableauAuth, Pager
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email import encoders
import pandas as pd
from functools import wraps
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader


# ============ 新增：PDF 二次处理 ============
try:
    from PyPDF2 import PdfReader, PdfWriter
except ImportError:
    raise ImportError("请安装 PyPDF2: pip install PyPDF2")

def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(f"{func.__name__}: {time.time() - start:.0f} seconds")
        return result
    return wrapper

class YTracker:
    def __init__(self, start_y, page_height, margin):
        self.current_y = start_y
        self.page_height = page_height
        self.margin = margin

    def add_text_height(self, line_count, line_height):
        height_used = line_count * line_height
        self.current_y -= height_used
        return height_used

    def add_fixed_height(self, height):
        self.current_y -= height
        return height

    def get_y(self):
        return self.current_y

    def set_y(self, y):
        self.current_y = y

    def check_new_page(self):
        """检查是否需要换页"""
        if self.current_y <= self.margin:
            return True
        return False

    def reset_for_new_page(self):
        """重置Y坐标为新页顶部"""
        self.current_y = self.page_height - self.margin

class SimplePDFDocument:
    def __init__(self, filename, pagesize, margin=50, font_name="semibold", font_size=20,header_size = 10,header=None, footer=None):
        """
        :param filename: PDF 文件名
        :param pagesize: 页面大小，如 A4, landscape(A4)
        :param margin: 边距
        :param font_name: 字体名（需已注册）
        :param font_size: 字号
        :param header_size 页眉字号
        :param header: 页眉文本，支持 {page} {total}，如 "第 {page} 页，共 {total} 页"
        :param footer: 页脚文本，支持 {page} {total}
        """
        self.filename = filename
        self.pagesize = pagesize
        self.margin = margin
        self.font_name = font_name
        self.font_size = font_size
        self.header_size = header_size
        self.line_height = font_size + 6
        self.width, self.height = pagesize
        self.text_width = self.width - 2 * margin

        # 页眉页脚
        self.header_text = header
        self.footer_text = footer

        # 创建临时画布
        self.c = canvas.Canvas(filename + ".tmp.pdf", pagesize=pagesize)
        self.c.setFont(font_name, font_size)

        # Y 坐标管理器
        self.y_tracker = YTracker(start_y=self.height - margin, page_height=self.height, margin=self.margin)

        # 清理零宽字符
        self._clean_text = lambda text: re.sub(r'[\u200b-\u200f\u202a-\u202e]', '', text)

        # 页面计数
        self.page_count = 0

        # 开始第一页
        self._start_new_page()

    def add_cover_page(self,title,subtitle=None,note=None,
                       title_font_size=36,subtitle_font_size=24,note_font_size=14,
                       title_font_name=None,subtitle_font_name=None,note_font_name=None):
        """
        添加封面页到当前页面（通常是第一页）
        """
        # 使用默认字体
        title_font_name = title_font_name or self.font_name
        subtitle_font_name = subtitle_font_name or self.font_name
        note_font_name = note_font_name or self.font_name

        # === 关键：不要 new_page()，直接使用当前页面 ===

        # 垂直居中布局
        center_y = self.height / 2
        line_spacing = 40

        y = center_y + line_spacing  # 主标题位置

        # 清除可能已有的内容（比如页眉/页脚占位）—— 可选
        # 实际上 canvas 没有“清除”，我们只需确保不提前画东西即可

        # 设置字体并绘制主标题
        self.c.setFont(title_font_name,title_font_size)
        title_width = self.c.stringWidth(title,title_font_name,title_font_size)
        x = (self.width - title_width) / 2
        self.c.drawString(x,y,title)

        # 副标题
        if subtitle:
            y -= line_spacing
            self.c.setFont(subtitle_font_name,subtitle_font_size)
            subtitle_width = self.c.stringWidth(subtitle,subtitle_font_name,subtitle_font_size)
            x = (self.width - subtitle_width) / 2
            self.c.drawString(x,y,subtitle)

        # 注释
        if note:
            y -= line_spacing * 1.5
            self.c.setFont(note_font_name,note_font_size)
            note_width = self.c.stringWidth(note,note_font_name,note_font_size)
            x = (self.width - note_width) / 2
            self.c.drawString(x,y,note)

        # 更新 Y 跟踪器，防止后续内容重叠
        self.y_tracker.set_y(y - 50)

        # ✅ 关键：手动标记当前页为“封面”，避免在 save() 中给封面加页眉页脚
        self.is_first_page_cover = True  # 添加标记
    def _start_new_page(self):
        """开始一个新页面"""
        if self.page_count > 0:
            self.c.showPage()

        self.page_count += 1
        self.c.setFont(self.font_name, self.font_size)
        self.y_tracker.reset_for_new_page()

        # # === 绘制页眉：放在最顶部中间 === 跟下边save()里边的重复了，先注释掉
        # if self.header_text:
        #     header = self.header_text.format(page=self.page_count, total="?")
        #     y_pos = self.height - self.margin + 25  # 调整 +10 控制上下位置
        #     self._draw_text_center(header, y_pos, font_size=self.font_size - 4)
        #
        # # === 绘制页脚占位（临时）===
        # if self.footer_text:
        #     footer = self.footer_text.format(page=self.page_count, total="?")
        #     self._draw_text_center(footer, self.margin - 15, font_size=self.font_size - 4)

    def _draw_text_center(self, text, y, font_size=None):
        """在主画布上居中绘制文本"""
        if font_size is None:
            font_size = self.font_size
        self.c.setFont(self.font_name, font_size)
        text_width = self.c.stringWidth(text, self.font_name, font_size)
        x = (self.width - text_width) / 2
        self.c.drawString(x, y, text)

    def _wrap_text(self, text, max_width):
        """返回文本的行列表"""
        from reportlab.pdfbase.pdfmetrics import stringWidth
        lines = []
        current_line = ""
        for char in text:
            test_line = current_line + char
            if stringWidth(test_line, self.font_name, self.font_size) <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = char
        if current_line:
            lines.append(current_line)
        return lines

    def _handle_new_page(self):
        """处理换页逻辑"""
        if self.y_tracker.check_new_page():
            self._start_new_page()

    def new_page(self):
        """手动插入新页面"""
        self._start_new_page()
        print(f"📄 已手动创建新页面 (第 {self.page_count} 页)")

    def add_paragraph(self, text, align="left"):
        self._handle_new_page()
        text = self._clean_text(text)
        lines = self._wrap_text(text, self.text_width)
        line_count = len(lines)

        x = self.margin
        if align == "center":
            x = (self.width - self.text_width) / 2
        elif align == "right":
            x = self.width - self.margin - self.text_width

        text_obj = self.c.beginText(x, self.y_tracker.get_y())
        text_obj.setFont(self.font_name, self.font_size)
        for line in lines:
            text_obj.textLine(line)
        self.c.drawText(text_obj)

        self.y_tracker.add_text_height(line_count, self.line_height)

    def add_image(self, image_path, width=300, align="left", space_after=18):
        self._handle_new_page()
        try:
            img = ImageReader(image_path)
            img_width, img_height = img.getSize()
            aspect = img_height / img_width
            display_width = width
            display_height = width * aspect

            x = self.margin
            if align == "center":
                x = (self.width - display_width) / 2
            elif align == "right":
                x = self.width - self.margin - display_width

            y = self.y_tracker.get_y() - display_height
            self.c.drawImage(image_path, x, y, width=display_width, height=display_height,
                             preserveAspectRatio=True, mask='auto')
            self.y_tracker.add_fixed_height(display_height + space_after)
        except Exception as e:
            print(f"[警告] 图片加载失败: {image_path}, 错误: {e}")
            self.y_tracker.add_fixed_height(100 + space_after)

    def add_spacing(self, height):
        self.y_tracker.add_fixed_height(height)

    def save(self):
        """保存 PDF，注入总页数"""
        self.c.save()
        temp_pdf = self.filename + ".tmp.pdf"

        # 如果没有页眉页脚，直接重命名
        if not self.header_text and not self.footer_text:
            os.rename(temp_pdf, self.filename)
            print(f"✅ PDF 已保存: {self.filename}")
            return

        # 读取临时 PDF
        reader = PdfReader(temp_pdf)
        total_pages = len(reader.pages)
        output = PdfWriter()

        # 为每一页注入页眉页脚
        for i in range(total_pages):
            page = reader.pages[i]
            from reportlab.pdfgen import canvas
            from io import BytesIO
            packet = BytesIO()
            c = canvas.Canvas(packet, pagesize=self.pagesize)

            # 设置字体
            try:
                c.setFont(self.font_name, self.font_size - 4)
            except Exception:
                c.setFont("Helvetica", self.font_size - 4)

            # === 绘制页眉：最顶部中间 ===
            if self.header_text:
                header = self.header_text.format(page=i+1, total=total_pages)
                y_pos = self.height - self.margin + 25
                self._draw_text_center_pdf(c, header, y_pos)

            # === 绘制页脚：底部中间 ===
            if self.footer_text:
                footer = self.footer_text.format(page=i+1, total=total_pages)
                y_pos = self.margin - 15
                self._draw_text_center_pdf(c, footer, y_pos)

            c.save()
            packet.seek(0)
            overlay = PdfReader(packet).pages[0]
            page.merge_page(overlay)
            output.add_page(page)

        # 写入最终文件
        with open(self.filename, "wb") as f:
            output.write(f)

        # 删除临时文件
        os.remove(temp_pdf)
        print(f"✅ PDF 已保存: {self.filename} (共 {total_pages} 页)")

    def _draw_text_center_pdf(self, c, text, y):
        """在外部 canvas 上居中绘制文本（安全版）"""
        font_name = self.font_name
        font_size = self.header_size # self.font_size - 4

        # 显式设置字体
        try:
            c.setFont(font_name, font_size)
        except Exception:
            c.setFont("Helvetica", font_size)

        # 使用一致的字体计算宽度
        actual_font = c._fontname
        actual_size = c._fontsize
        text_width = c.stringWidth(text, actual_font, actual_size)
        x = (self.width - text_width) / 2
        c.drawString(x, y, text)

class AllTool:

    @staticmethod
    @timer
    def connect_db(sql_code, col, host, user, password, port):
        config = {
            'host': host,
            'user': user,
            'password': password,
            'port': port,
            'charset': 'utf8mb4',
            'autocommit': True
        }
        conn = None
        try:
            conn = pymysql.connect(**config)
            with conn.cursor() as cursor:
                cursor.execute(sql_code)
                rows = cursor.fetchall()
                df = pd.DataFrame(rows, columns=col)
                df.fillna(0, inplace=True)
                return df
        except Exception as e:
            print(f"❌ DB Error: {e}")
            return pd.DataFrame(columns=col)
        finally:
            if conn:
                conn.close()

    @staticmethod
    def send_file(filepath,key):
        url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/upload_media?key={}&type=file".format(key)
        webhook = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={}'.format(key)
        filename = os.path.basename(filepath)
        with open(filepath,'rb') as f:
            files = {
                'media':(filename,f,'application/octet-stream')
            }
            r = requests.post(url,files=files)
        r_data = json.loads(r.text)
        media_id = r_data.get('media_id')
        header = {'Content-Type':'application/json'}
        response = requests.post(webhook,headers=header,json={
            'msgtype':'file',
            'file':{'media_id':media_id}})
        print(f'{filename} has been sent successfully')

    @staticmethod
    def send_excel_sheets_as_images(excel_file, sheet_list, wx_key, prefix=""):
        for sheet_name in sheet_list:
            png_file = f"{sheet_name}.png"
            try:
                print(f"📊 Exporting {sheet_name} to {png_file}")
                excel2img.export_img(excel_file, png_file, sheet_name, None)
                with open(png_file, 'rb') as f:
                    data = f.read()
                    base64_str = base64.b64encode(data).decode('utf-8')
                    md5_str = hashlib.md5(data).hexdigest()
                payload = {
                    "msgtype": "image",
                    "image": {"base64": base64_str, "md5": md5_str}
                }
                url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={wx_key}"
                headers = {'Content-Type': 'application/json'}
                res = requests.post(url, json=payload, headers=headers)
                result = res.json()
                if result.get('errcode') == 0:
                    print(f"✅ {prefix}-{sheet_name}.png sent successfully.")
                else:
                    print(f"❌ Send failed: {result.get('errmsg')}")
            except Exception as e:
                print(f"❌ Error processing {sheet_name}: {e}")
            finally:
                if os.path.exists(png_file):
                    try:
                        os.remove(png_file)
                        print(f"🗑️ {png_file} deleted.")
                    except Exception as e:
                        print(f"❌ Cleanup error: {e}")

    @staticmethod
    def out_img(excel_file,sheet_list):
        try:
            print('begin ...')
            for i in range(len(sheet_list)):
                excel2img.export_img(excel_file,sheet_list[i] + '.png',sheet_list[i],None)
        except Exception as e:
            print('fail!',e)

    @staticmethod
    def send_picture(filename_picture,wx_api_key):
        wx_url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={}'.format(wx_api_key)
        with open(filename_picture,'rb') as f:
            fd = f.read()
            base64content = str(base64.b64encode(fd),"utf-8")
            md = hashlib.md5()
            md.update(fd)
            md5content = md.hexdigest()
        headers = {'Content-Type':'application/json'}
        msg = {"msgtype":"image","image":{"base64":base64content,"md5":md5content}}
        try:
            result = requests.post(url=wx_url,headers=headers,json=msg)
            print(result.text)
        except Exception as e:
            print("request error",e)

    @staticmethod
    def export_excel(view,download_dir):
        try:
            view.server.views.populate_excel(view)
            excel_path = os.path.join(download_dir,
                                      f"{view.name.replace('/','_')}{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx")
            with open(excel_path,"wb") as f:
                f.write(b''.join(view.excel))
            print(f"✅ 交叉表Excel已保存: {excel_path}")
            return excel_path
        except Exception as e:
            print(f"❌ 交叉表Excel下载失败: {str(e)}")
            return f"失败: {str(e)}"

    @staticmethod
    def export_pdf(view,download_dir):
        try:
            view.server.views.populate_pdf(view)
            pdf_path = os.path.join(download_dir,f"{view.name.replace('/','_')}.pdf")
            with open(pdf_path,"wb") as f:
                f.write(view.pdf)
            print(f"✅ PDF已保存: {pdf_path}")
            return pdf_path
        except Exception as e:
            print(f"❌ PDF下载失败: {str(e)}")
            return f"失败: {str(e)}"

    @staticmethod
    def export_image(view,download_dir):
        try:
            view.server.views.populate_image(view)
            img_path = os.path.join(download_dir,f"{view.name.replace('/','_')}.png")
            with open(img_path,"wb") as f:
                f.write(view.image)
            print(f"✅ 图片已保存: {img_path}")
            return img_path
        except Exception as e:
            print(f"❌ 图片下载失败: {str(e)}")
            return f"失败: {str(e)}"

    @staticmethod
    def find_view_by_names(server,workbook_name,view_name):
        """
        通过工作簿名称和视图名称查找视图对象
        """
        for wb in Pager(server.workbooks):
            if wb.name == workbook_name:
                server.workbooks.populate_views(wb)
                for view in wb.views:
                    if view.name == view_name:
                        # 获取完整视图对象
                        full_view = server.views.get_by_id(view.id)
                        full_view.server = server
                        return full_view
        print(f"❌ 未找到视图: {workbook_name} / {view_name}")
        return None

    @staticmethod
    def export_tableau_views_by_name(server_url,username,password,site_name,wb_view_pairs,export_types,download_dir = "unname"):
        if not isinstance(wb_view_pairs,list) or not wb_view_pairs:
            raise ValueError("wb_view_pairs 必须为非空列表")
        if not isinstance(export_types,list) or not export_types:
            raise ValueError("export_types 必须为非空列表")

        print("1. 初始化服务器连接...")
        server = Server(server_url,use_server_version=True)
        auth = TableauAuth(username=username,password=password,site_id=site_name)
        results = {}

        try:
            with server.auth.sign_in(auth):
                print("✅ 登录成功")
                os.makedirs(download_dir,exist_ok=True)

                for pair in wb_view_pairs:
                    workbook_name = pair["workbook_name"]
                    view_name = pair["view_name"]
                    view_result = {}

                    view = AllTool.find_view_by_names(server,workbook_name,view_name)
                    if not view:
                        view_result['error'] = f"未找到视图: {workbook_name} / {view_name}"
                        results[f"{workbook_name}:{view_name}"] = view_result
                        continue

                    print(f"\n正在处理视图: {view.name} (ID: {view.id})")

                    if 0 in export_types:
                        view_result['excel'] = AllTool.export_excel(view,download_dir)
                    if 1 in export_types:
                        view_result['pdf'] = AllTool.export_pdf(view,download_dir)
                    if 2 in export_types:
                        view_result['image'] = AllTool.export_image(view,download_dir)

                    results[f"{workbook_name}:{view_name}"] = view_result

        except Exception as e:
            print(f"❌ 发生异常: {str(e)}")
            traceback.print_exc()
        finally:
            print("6. 登出Tableau Server...")
            try:
                server.auth.sign_out()
                print("🚪 已登出")
            except Exception:
                pass
        return results

    @staticmethod
    def send_email(sender,area_email,filename,subject,attachment,html_body,tf_attached,cc_list=None,image_path=None):
        """
        send_email
        :param area_email: （str or list）
        :param sender:dir
        :param subject: main_title
        :param attachment:attachment filename
        :param filename: attachment filepath
        :param tf_attached: tf_attached
        :param cc_list: cc_list
        :param image_path: image_path
        """
        port = sender['port']
        smtp_server = sender['smtp_server']
        sender_email = sender['sender_email']
        password = sender['password']

        to_list = area_email if isinstance(area_email,list) else [area_email]
        to_str = ', '.join(to_list)

        cc_list = cc_list or []
        if isinstance(cc_list,str):
            cc_list = [cc_list]
        cc_str = ', '.join(cc_list)

        message = MIMEMultipart('related')
        message['From'] = sender_email
        message['To'] = to_str
        if cc_list:
            message['Cc'] = cc_str
        message['Subject'] = subject
        html_body = html_body
        part_html = MIMEText(html_body,'html','utf-8')
        message.attach(part_html)

        if image_path and os.path.exists(image_path):
            try:
                with open(image_path,'rb') as img_file:
                    img = MIMEImage(img_file.read())
                img.add_header('Content-ID','<image>')
                img.add_header('Content-Disposition','inline',filename=os.path.basename(image_path))
                message.attach(img)
                print(f"🖼️  已内嵌图片：{image_path}")
            except Exception as e:
                print(f"❌ 嵌入图片失败：{e}")
        else:
            if image_path:
                print(f"❌ 内嵌图片文件不存在：{image_path}")

        if tf_attached:
            if not os.path.exists(filename):
                print(f"❌ 附件文件不存在：{filename}")
                return
            try:
                with open(filename,'rb') as f:
                    part = MIMEBase('application','octet-stream')
                    part.set_payload(f.read())
                encoders.encode_base64(part)
                safe_filename = attachment
                part.add_header(
                    'Content-Disposition',
                    'attachment',
                    filename=safe_filename
                )
                message.attach(part)
                print(f"📎 已添加附件：{filename}")
            except Exception as e:
                print(f"❌ 添加附件失败：{e}")
                return

        all_recipients = to_list + cc_list
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        try:
            with smtplib.SMTP_SSL(smtp_server,port,context=context) as server:
                server.login(sender_email,password)
                print("✅ 登录邮件服务器成功")
                server.sendmail(sender_email,all_recipients,message.as_string())
                print(f"✅ 邮件已发送至：收件人={to_str}, 抄送={cc_str if cc_list else '无'}")
        except Exception as e:
            print(f"❌ 发送邮件失败：{e}")
