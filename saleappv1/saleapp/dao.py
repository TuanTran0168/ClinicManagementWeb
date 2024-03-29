from saleapp.models import *
from saleapp import db
from flask_login import current_user
from sqlalchemy import func
import hashlib

from sqlalchemy.sql.functions import user


def load_diseases():
    return Benh.query.all()


def load_categories():
    return DanhMucThuoc.query.all()


def load_users():
    return User.query.all()

def load_users_in_register():
    query = db.session.query(User.id, User.tenUser, User.tenDangNhap)
    return query.all()

def load_users_by_phone_number(so_dien_thoai=None):
    query = db.session.query(User.id, User.tenUser, User.soDienThoai)
    if so_dien_thoai:
        query = query.filter(User.soDienThoai.__eq__(so_dien_thoai))
    return query.all()


def load_products(danhMucThuoc_id=None, kw=None):
    query = Thuoc.query.filter(Thuoc.trangThai.__eq__(True))

    if danhMucThuoc_id:
        query = query.filter(Thuoc.danhMucThuoc_id.__eq__(danhMucThuoc_id))

    if kw:
        query = query.filter(Thuoc.tenThuoc.contains(kw))

    return query.all()


def get_product_by_id(product_id):
    return Thuoc.query.get(product_id)


def auth_user(username, password):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

    return User.query.filter(User.tenDangNhap.__eq__(username.strip()),
                             User.matKhau.__eq__(password)).first()


def register(name, username, password, birthday, gender, telephone, address, avatar):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    u = User(tenUser=name, tenDangNhap=username.strip(), matKhau=password, ngaySinh=birthday, gioiTinh=gender,
             soDienThoai=telephone, diaChi=address, anhDaiDien=avatar)
    db.session.add(u)
    db.session.commit()


def get_user_by_id(user_id):
    return User.query.get(user_id)


def add_receipt(cart):
    if cart:
        r = PhieuKham(user=current_user)
        db.session.add(r)

        for c in cart.values():
            d = ChiTietPhieuKham(quantity=c['quantity'], price=c['price'],
                                 receipt=r, product_id=c['id'])
            db.session.add(d)

        db.session.commit()


def count_product_by_cate():
    return db.session.query(DanhMucThuoc.id, DanhMucThuoc.tenDanhMuc, func.count(Thuoc.id)) \
        .join(Thuoc, Thuoc.danhMucThuoc_id.__eq__(DanhMucThuoc.id), isouter=True) \
        .group_by(DanhMucThuoc.id).order_by(-DanhMucThuoc.tenDanhMuc).all()


def count_user_by_role(userRoleStats):
    if userRoleStats:
        count = 0
        for r1 in userRoleStats.values():
            for r2 in userRoleStats.values():
                if r1.__eq__(r2):
                    count = count + 1
    return count


def count_user():
    return db.session.query(User.user_role, func.count(User.id)).group_by(User.user_role).all()

def count_user_in_register():
    return db.session.query(func.count(User.id)).all()

def stats_revenue_by_user(kw=None, from_date=None, to_date=None):
    query = db.session.query(User.tenUser, PhieuKham.ngayKham, func.sum(ChiTietPhieuKham.soLuongThuoc * Thuoc.giaThuoc)) \
        .join(PhieuKham, PhieuKham.id.__eq__(ChiTietPhieuKham.phieuKham_id)) \
        .join(Thuoc, Thuoc.id.__eq__(ChiTietPhieuKham.Thuoc_id))

    if kw:
        query = query.filter(Thuoc.tenThuoc.contains(kw))

    if from_date:
        query = query.filter(PhieuKham.ngayKham.__ge__(from_date))

    if to_date:
        query = query.filter(PhieuKham.ngayKham.__le__(to_date))

    return query.group_by(User.tenUser, PhieuKham.ngayKham).all()


# def stats_revenue_by_prod(kw=None, from_date=None, to_date=None):
#     query = db.session.query(PhieuKham.ngayKham, func.count(ChiTietDanhSachKham.id),  \
#                              func.sum(ChiTietPhieuKham.soLuongThuoc * Thuoc.giaThuoc)) \
#         .join(Thuoc, Thuoc.id.__eq__(ChiTietPhieuKham.Thuoc_id), isouter=True)
#
#     if kw:
#         query = query.filter(Thuoc.tenThuoc.contains(kw))
#
#     if from_date:
#         query = query.filter(PhieuKham.ngayKham.__ge__(from_date))
#
#     if to_date:
#         query = query.filter(PhieuKham.ngayKham.__le__(to_date))
#
#     return query.group_by(Thuoc.id, ChiTietPhieuKham.soLuongThuoc ).order_by(Thuoc.id).all()

# Bản gốc của thống kê báo cáo thuốc
# def stats_by_medic(kw=None, from_date=None, to_date=None):
#     query = db.session.query(Thuoc.id, Thuoc.tenThuoc, Thuoc.donViThuoc, ChiTietPhieuKham.soLuongThuoc,
#                              ChiTietPhieuKham.phieuKham_id, \
#                              func.sum(ChiTietPhieuKham.soLuongThuoc * Thuoc.giaThuoc)) \
#         .join(Thuoc, Thuoc.id.__eq__(ChiTietPhieuKham.Thuoc_id), isouter=True)
#
#     if kw:
#         query = query.filter(Thuoc.tenThuoc.contains(kw))
#
#     if from_date:
#         query = query.filter(PhieuKham.ngayKham.__ge__(from_date))
#
#     if to_date:
#         query = query.filter(PhieuKham.ngayKham.__le__(to_date))
#
#     return query.group_by(Thuoc.id, ChiTietPhieuKham.phieuKham_id, ChiTietPhieuKham.soLuongThuoc).order_by(
#         ChiTietPhieuKham.phieuKham_id, Thuoc.id).all()

# Hàng thử nghiệm của thống kê báo cáo thuốc (Thành công, thành hàng real)
def stats_by_medic(kw=None, from_date=None, to_date=None):
    query = db.session.query(Thuoc.id, Thuoc.tenThuoc, Thuoc.donViThuoc,
                             func.sum(ChiTietPhieuKham.soLuongThuoc)) \
        .join(Thuoc, Thuoc.id.__eq__(ChiTietPhieuKham.Thuoc_id), isouter=True)

    if kw:
        query = query.filter(Thuoc.tenThuoc.contains(kw))

    if from_date:
        query = query.filter(PhieuKham.ngayKham.__ge__(from_date))

    if to_date:
        query = query.filter(PhieuKham.ngayKham.__le__(to_date))

    return query.group_by(Thuoc.id).order_by(-Thuoc.id).all()


# Ngày, số bệnh nhân, doanh thu
# Tên bệnh nhân, số tiền
def stats_by_revenue(month=None):
    # HoaDon, User
    query = db.session.query(HoaDon.ngayKham, func.count(User.id), func.sum(HoaDon.tongTien)).join(HoaDon,
                                                                                                   HoaDon.user_id.__eq__(
                                                                                                       User.id))
    if month:
        query = query.filter(HoaDon.ngayKham.contains(month))

    return query.group_by(HoaDon.ngayKham).all()


# ====================================================================================

# Bản gốc của tính hóa đơn
# def bill():
#     query = db.session.query(PhieuKham.id,func.sum(ChiTietPhieuKham.soLuongThuoc * Thuoc.giaThuoc) ) \
#         .join(PhieuKham, PhieuKham.id.__eq__(ChiTietPhieuKham.phieuKham_id))\
#         .join(Thuoc, Thuoc.id.__eq__(ChiTietPhieuKham.Thuoc_id))
#
#     return query.group_by(PhieuKham.id).order_by(PhieuKham.id).all()


# Bản mới của tính hóa đơn (Xịn hơn, Xài cái này) | Bill này tính toàn bộ bill luôn
def bill():
    query = db.session.query(User.id, User.tenUser, PhieuKham.id, PhieuKham.user_id,
                             func.sum(ChiTietPhieuKham.soLuongThuoc * Thuoc.giaThuoc)) \
        .join(PhieuKham, PhieuKham.id.__eq__(ChiTietPhieuKham.phieuKham_id)) \
        .join(Thuoc, Thuoc.id.__eq__(ChiTietPhieuKham.Thuoc_id)) \
        .join(User, User.id.__eq__(PhieuKham.user_id))

    return query.group_by(User.id, PhieuKham.id).order_by(User.id, PhieuKham.id).all()


# def bill_for_one_user_by_id(user_id):
#     query = db.session.query(User.id, User.tenUser, PhieuKham.id, PhieuKham.user_id,
#                              func.sum(ChiTietPhieuKham.soLuongThuoc * Thuoc.giaThuoc)) \
#         .join(PhieuKham, PhieuKham.id.__eq__(ChiTietPhieuKham.phieuKham_id)) \
#         .join(Thuoc, Thuoc.id.__eq__(ChiTietPhieuKham.Thuoc_id)) \
#         .join(User, User.id.__eq__(PhieuKham.user_id))
#
#     query = query.filter(User.id.__eq__(user_id))
#
#     return query.group_by(User.id, PhieuKham.id).first()

def bill_for_one_user_by_id(user_id):
    query = db.session.query(User.id, User.tenUser, PhieuKham.id, PhieuKham.user_id,
                             func.sum(ChiTietPhieuKham.soLuongThuoc * Thuoc.giaThuoc), PhieuKham.ngayKham) \
        .join(PhieuKham, PhieuKham.id.__eq__(ChiTietPhieuKham.phieuKham_id)) \
        .join(Thuoc, Thuoc.id.__eq__(ChiTietPhieuKham.Thuoc_id)) \
        .join(User, User.id.__eq__(PhieuKham.user_id))

    query = query.filter(User.id.__eq__(user_id))
    today = datetime.now()
    todayString = str(today)[0:10]
    query = query.filter(PhieuKham.ngayKham.__eq__(todayString))

    return query.group_by(User.id, PhieuKham.id, PhieuKham.ngayKham).first()
def save_bill_for_user(ngayKham, tongTien, user_id):
    b = HoaDon(ngayKham=ngayKham, tongTien=tongTien, user_id=user_id)
    db.session.add(b)
    db.session.commit()


def load_medical_form_today():
    d = datetime.now()
    s = str(d)[5:10]

    query = db.session.query(PhieuKham.id, PhieuKham.tenPhieuKham, PhieuKham.ngayKham, PhieuKham.trieuChung,
                             PhieuKham.chuanDoan, PhieuKham.user_id)
    query = query.filter(PhieuKham.ngayKham.contains(s))
    return query.all()


def load_hoa_don_by_phieu_kham_id(phieu_kham_id=None):  # Viết cái câu truy vấn ngon lành mà không xài được tức ghê -_-
    query = db.session.query(User.tenUser, HoaDon.ngayKham, HoaDon.tongTien) \
        .join(HoaDon, HoaDon.user_id.__eq__(User.id)) \
        .join(PhieuKham, PhieuKham.user_id.__eq__(User.id))

    today = datetime.now()
    todayString = str(today)[0:10]
    query = query.filter(HoaDon.ngayKham.__eq__(todayString))

    if phieu_kham_id:
        query = query.filter(PhieuKham.id.__eq__(phieu_kham_id))

    return query.group_by(User.tenUser, HoaDon.ngayKham, HoaDon.tongTien).all()


def load_hoa_don():
    query = db.session.query(HoaDon.id, PhieuKham.id, User.tenUser, HoaDon.ngayKham, HoaDon.tongTien) \
        .join(HoaDon, HoaDon.user_id.__eq__(User.id)) \
        .join(PhieuKham, PhieuKham.user_id.__eq__(User.id))

    today = datetime.now()
    todayString = str(today)[0:10]
    query = query.filter(HoaDon.ngayKham.__eq__(todayString))
    query = query.filter(PhieuKham.ngayKham.__eq__(todayString))

    return query.group_by(HoaDon.id, PhieuKham.id, User.tenUser, HoaDon.ngayKham, HoaDon.tongTien).order_by(HoaDon.id).all()


# ====================================================================================

# def load_medical_form_for_one_user_today_by_phieuKham_id(phieuKham_id):
#     d = datetime.now
#     s = str(d)[0:10]
#
#     query = db.session.query(PhieuKham.id, PhieuKham.tenPhieuKham, PhieuKham.ngayKham, PhieuKham.trieuChung, PhieuKham.chuanDoan, PhieuKham.user_id)
#     query = query.filter(PhieuKham.ngayKham.contains(s)) #Chưa so sánh được ngày
#     query = query.filter(PhieuKham.id.__eq__(phieuKham_id))
#     return query.all()

def load_medical_form_for_one_user_by_phieuKham_id(phieuKham_id):
    d = datetime.now()
    s = str(d)[5:10]

    query = db.session.query(PhieuKham.id, PhieuKham.tenPhieuKham, PhieuKham.ngayKham, PhieuKham.trieuChung,
                             PhieuKham.chuanDoan, PhieuKham.user_id)
    query = query.filter(PhieuKham.id.__eq__(phieuKham_id))
    return query.all()


# return User.query.filter(User.tenDangNhap.__eq__(username.strip()),
#                              User.matKhau.__eq__(password)).first()

# def bill():
#     query = db.session.query(PhieuKham.id, func.sum(func.sum(ChiTietPhieuKham.soLuongThuoc * Thuoc.giaThuoc))) \
#         .join(ChiTietPhieuKham, ChiTietPhieuKham.Thuoc_id.__eq__(Thuoc.id)) \
#         .join(ChiTietPhieuKham, ChiTietPhieuKham.phieuKham_id.__eq__(PhieuKham.id))\
#
#     return query.group_by(PhieuKham.id).order_by(PhieuKham.id).all()


def load_danh_sach_kham():
    return db.session.query(DanhSachKham.id, DanhSachKham.tenDanhSachKham, DanhSachKham.ngayKham).all()


def create_danh_sach_kham(create):
    if create.__eq__("Tạo danh sách"):
        dsk = DanhSachKham(ngayKham=datetime.now())
        db.session.add(dsk)
        db.session.commit()


def load_danh_sach_kham_by_today():
    query = db.session.query(DanhSachKham.id, DanhSachKham.tenDanhSachKham, DanhSachKham.ngayKham)
    today = datetime.now()
    todayString = str(today)[0:10]
    query = query.filter(DanhSachKham.ngayKham.__eq__(todayString))
    return query.all()


def save_chi_tiet_danh_sach_kham(danh_sach_kham_id, user_id):
    ctdsk = ChiTietDanhSachKham(danhSachKham_id=danh_sach_kham_id, user_id=user_id)
    db.session.add(ctdsk)
    db.session.commit()


def load_chi_tiet_danh_sach_kham_today(user_id=None):
    query = db.session.query(ChiTietDanhSachKham.id, ChiTietDanhSachKham.danhSachKham_id, ChiTietDanhSachKham.user_id) \
        .join(DanhSachKham, DanhSachKham.id.__eq__(ChiTietDanhSachKham.danhSachKham_id))
    today = datetime.now()
    todayString = str(today)[0:10]
    query = query.filter(DanhSachKham.ngayKham.__eq__(todayString))

    if user_id:
        query = query.filter(ChiTietDanhSachKham.user_id.__eq__(user_id))

    return query.all()


def get_user_in_danh_sach_kham_by_danh_sach_kham_id(danh_sach_kham_id=None):  # FAIL
    query = db.session.query(DanhSachKham.id, ChiTietDanhSachKham.id, User.id, User.tenUser, User.gioiTinh,
                             User.ngaySinh, User.diaChi, User.soDienThoai) \
        .join(User, User.id.__eq__(ChiTietDanhSachKham.user_id)) \
        .join(DanhSachKham, DanhSachKham.id.__eq__(ChiTietDanhSachKham.id))

    # query = db.session.query(ChiTietDanhSachKham.id)\
    #         .join(User, User.id.__eq__(ChiTietDanhSachKham.user_id))\
    #         .join(DanhSachKham, DanhSachKham.id.__eq__(ChiTietDanhSachKham.id))

    if danh_sach_kham_id:
        query = query.filter(ChiTietDanhSachKham.danhSachKham_id.__eq__(danh_sach_kham_id))

    return query.order_by(ChiTietDanhSachKham.id).all()


# def get_user_in_danh_sach_kham_today():
#     query = db.session.query(ChiTietDanhSachKham.danhSachKham_id, ChiTietDanhSachKham.id, User.id, User.tenUser, User.gioiTinh, User.ngaySinh, User.diaChi, User.soDienThoai)\
#             .join(User, User.id.__eq__(ChiTietDanhSachKham.user_id))\
#             .join(DanhSachKham, DanhSachKham.id.__eq__(ChiTietDanhSachKham.id))
#
#     # today = datetime.now()
#     # todayString = str(today)[0:10]
#     # query = query.filter(DanhSachKham.ngayKham.__eq__(todayString))
#
#     return query.order_by(DanhSachKham.id).all()

# ====================================================================================
def get_user_in_danh_sach_kham():
    query = db.session.query(ChiTietDanhSachKham.id, ChiTietDanhSachKham.danhSachKham_id, User.id, User.tenUser,
                             User.gioiTinh, User.ngaySinh, User.diaChi, User.soDienThoai) \
        .join(User, User.id.__eq__(ChiTietDanhSachKham.user_id))

    return query.all()


def get_user_in_danh_sach_kham_today():
    query = db.session.query(ChiTietDanhSachKham.id, ChiTietDanhSachKham.danhSachKham_id, User.id, User.tenUser,
                             User.gioiTinh, User.ngaySinh, User.diaChi, User.soDienThoai) \
        .join(User, User.id.__eq__(ChiTietDanhSachKham.user_id))

    today = datetime.now()
    todayString = str(today)[0:10]
    query = query.filter(DanhSachKham.ngayKham.__eq__(todayString))
    return query.all()


# Lấy danh sách khám hôm nay ra()
# Lấy chi tiết danh sách khám hôm nay(id của danh sách hôm nay)
# Lấy các user trong chi tiết danh sách đó (bằng id của user trong chi tiết đó)
def load_DSK_today():
    query = db.session.query(DanhSachKham.id, DanhSachKham.tenDanhSachKham, DanhSachKham.ngayKham)
    today = datetime.now()
    todayString = str(today)[0:10]
    query = query.filter(DanhSachKham.ngayKham.__eq__(todayString))
    return query.all()


def load_chi_tiet_DSK_today(danh_sach_kham_id):
    query = db.session.query(ChiTietDanhSachKham.id, ChiTietDanhSachKham.danhSachKham_id, ChiTietDanhSachKham.user_id)
    if danh_sach_kham_id:
        query = query.filter(ChiTietDanhSachKham.danhSachKham_id.__eq__(danh_sach_kham_id))
    return query.all()


def load_users_by_user_id(user_id=None):
    query = db.session.query(User.id, User.tenUser,
                             User.gioiTinh, User.ngaySinh, User.diaChi, User.soDienThoai)

    if user_id:
        query = query.filter(User.id.__eq__(user_id))
    return query.all()


# ====================================================================================

def load_comments(product_id):
    return Comment.query.filter(Comment.product_id.__eq__(product_id)).order_by(-Comment.id).all()


def save_comment(product_id, content):
    c = Comment(content=content, product_id=product_id, user=current_user)
    db.session.add(c)
    db.session.commit()

    return c


def load_chi_tiet_DSK():
    query = db.session.query(ChiTietDanhSachKham.id, ChiTietDanhSachKham.danhSachKham_id, ChiTietDanhSachKham.user_id)

    return query.all()


# ====================================================================================
def create_phieu_kham_auto(user_id=None):
    pk = PhieuKham(user_id=user_id)
    db.session.add(pk)
    db.session.commit()


def load_phieu_kham_today_by_user_id(user_id=None):
    query = db.session.query(PhieuKham.id, PhieuKham.tenPhieuKham, PhieuKham.ngayKham, PhieuKham.trieuChung,
                             PhieuKham.chuanDoan, PhieuKham.user_id)

    today = datetime.now()
    todayString = str(today)[0:10]
    query = query.filter(PhieuKham.ngayKham.__eq__(todayString))

    if user_id:
        query = query.filter(PhieuKham.user_id.__eq__(user_id))

    return query.all()


def load_phieu_kham():
    query = db.session.query(PhieuKham.id, PhieuKham.tenPhieuKham, PhieuKham.ngayKham, PhieuKham.trieuChung,
                             PhieuKham.chuanDoan, PhieuKham.user_id, User.tenUser).join(User, User.id.__eq__(
        PhieuKham.user_id))
    today = datetime.now()
    todayString = str(today)[0:10]
    query = query.filter(PhieuKham.ngayKham.__eq__(todayString))

    return query.all()


def load_phieu_kham(user_id=None):
    query = db.session.query(PhieuKham.id, PhieuKham.tenPhieuKham, PhieuKham.ngayKham, PhieuKham.trieuChung,
                             PhieuKham.chuanDoan, PhieuKham.user_id, User.tenUser).join(User, User.id.__eq__(
        PhieuKham.user_id))
    today = datetime.now()
    todayString = str(today)[0:10]
    query = query.filter(PhieuKham.ngayKham.__eq__(todayString))

    if user_id:
        query = query.filter(PhieuKham.user_id.__eq__(user_id))

    return query.all()


def load_phieu_kham_today_by_phieu_kham_id(phieu_kham_id=None):
    query = db.session.query(PhieuKham.id, PhieuKham.tenPhieuKham, PhieuKham.ngayKham, PhieuKham.trieuChung,
                             PhieuKham.chuanDoan, PhieuKham.user_id, User.tenUser).join(User, User.id.__eq__(
        PhieuKham.user_id))
    today = datetime.now()
    todayString = str(today)[0:10]
    query = query.filter(PhieuKham.ngayKham.__eq__(todayString))

    if phieu_kham_id:
        query = query.filter(PhieuKham.id.__eq__(phieu_kham_id))

    return query.all()


# ====================================================================================
def load_medicines():
    return Thuoc.query.all()


def load_medicines_by_name(ten_thuoc=None):
    query = db.session.query(Thuoc.id, Thuoc.tenThuoc, Thuoc.giaThuoc, Thuoc.donViThuoc, Thuoc.moTa,
                             Thuoc.danhMucThuoc_id)
    if ten_thuoc:
        query = query.filter(Thuoc.tenThuoc.__eq__(ten_thuoc))

    return query.all()


def save_chi_tiet_phieu_kham(so_luong_thuoc=None, thuoc_id=None, phieu_kham_id=None):
    ctpk = ChiTietPhieuKham(soLuongThuoc=so_luong_thuoc, Thuoc_id=thuoc_id, phieuKham_id=phieu_kham_id)
    db.session.add(ctpk)
    db.session.commit()


# def update_phieu_kham(phieu_kham_id=None, trieu_chung=None, chuan_doan=None):
#     query = db.session.query(PhieuKham.id, PhieuKham.tenPhieuKham, PhieuKham.ngayKham, PhieuKham.trieuChung,
#                              PhieuKham.chuanDoan, PhieuKham.user_id)
#
#     if phieu_kham_id:
#         query = query.filter(PhieuKham.id.__eq__(phieu_kham_id))
#         query.trieuChung = trieu_chung
#         query.chuanDoan = chuan_doan
#
#     db.session.commit()
#     return query.all()


def update_phieu_kham(phieu_kham_id=None, trieu_chung=None, chuan_doan=None):
    phieu_kham = PhieuKham.query.filter_by(id=phieu_kham_id).first()
    phieu_kham.trieuChung = trieu_chung
    phieu_kham.chuanDoan = chuan_doan

    db.session.commit()


def load_phieu_kham_id_today_by_phieu_kham_id(phieu_kham_id=None):
    query = db.session.query(PhieuKham.id)
    today = datetime.now()
    todayString = str(today)[0:10]
    query = query.filter(PhieuKham.ngayKham.__eq__(todayString))

    if phieu_kham_id:
        query = query.filter(PhieuKham.id.__eq__(phieu_kham_id))

    return query.all()


def load_thuoc_in_chi_tiet_phieu_kham_today(user_id=None):
    query = db.session.query(Thuoc.id, Thuoc.tenThuoc, Thuoc.donViThuoc, ChiTietPhieuKham.soLuongThuoc, Thuoc.moTa,
                             ChiTietPhieuKham.phieuKham_id) \
        .join(Thuoc, Thuoc.id.__eq__(ChiTietPhieuKham.Thuoc_id)) \
        .join(PhieuKham, PhieuKham.id.__eq__(ChiTietPhieuKham.phieuKham_id))

    today = datetime.now()
    todayString = str(today)[0:10]
    query = query.filter(PhieuKham.ngayKham.__eq__(todayString))

    if user_id:
        query = query.filter(PhieuKham.user_id.__eq__(user_id))

    return query.all()


# ====================================================================================

def create_lich_su_benh(user_id):
    lsb = LichSuBenh(user_id=user_id)
    db.session.add(lsb)
    db.session.commit()


def load_lich_su_benh(user_id=None):
    query = db.session.query(LichSuBenh.id, LichSuBenh.tenLichSuBenh, LichSuBenh.user_id)

    if user_id:
        query = query.filter(LichSuBenh.user_id.__eq__(user_id))

    return query.all()


def save_chi_tiet_lich_su_benh(lich_su_benh_id=None, benh_id=None):
    lsb = ChiTietLichSuBenh(lichSuBenh_id=lich_su_benh_id, benh_id=benh_id)
    db.session.add(lsb)
    db.session.commit()


def load_benh_id_by_ten_benh(ten_benh=None):
    query = db.session.query(Benh.id)

    if ten_benh:
        query = query.filter(Benh.tenBenh.__eq__(ten_benh))

    return query.all()


def load_lich_su_benh_id_by_phieu_kham_id(phieu_kham_id=None):
    query = db.session.query(LichSuBenh.id) \
        .join(User, User.id.__eq__(LichSuBenh.user_id)) \
        .join(PhieuKham, PhieuKham.user_id.__eq__(User.id))

    if phieu_kham_id:
        query = query.filter(PhieuKham.id.__eq__(phieu_kham_id))

    return query.group_by(LichSuBenh.id).all()


# ====================================================================================
def load_lich_su_benh_in_view(user_id=None):
    query = db.session.query(LichSuBenh.id, LichSuBenh.user_id, User.tenUser, PhieuKham.ngayKham, PhieuKham.chuanDoan) \
        .join(User, User.id.__eq__(LichSuBenh.user_id)) \
        .join(PhieuKham, PhieuKham.user_id.__eq__(User.id))
    if user_id:
        query = query.filter(User.id.__eq__(user_id))

    return query.all()

def load_lich_su_benh_in_view_doctor(user_id=None):
    query = db.session.query(LichSuBenh.id, LichSuBenh.user_id, User.tenUser, PhieuKham.ngayKham, PhieuKham.chuanDoan) \
        .join(User, User.id.__eq__(LichSuBenh.user_id)) \
        .join(PhieuKham, PhieuKham.user_id.__eq__(User.id))
    if user_id:
        query = query.filter(User.id.__eq__(user_id))

    return query.all()

# ====================================================================================
def count_user_in_danh_sach_kham_today():
    query = db.session.query(DanhSachKham.id, func.count(ChiTietDanhSachKham.id))\
        .join(ChiTietDanhSachKham, ChiTietDanhSachKham.danhSachKham_id.__eq__(DanhSachKham.id))

    today = datetime.now()
    todayString = str(today)[0:10]
    query = query.filter(DanhSachKham.ngayKham.__eq__(todayString))

    return query.group_by(DanhSachKham.id).all()
# ====================================================================================
if __name__ == '__main__':
    from saleapp import app

    with app.app_context():
        # a = load_medical_form_for_one_user_by_phieuKham_id(1)
        # print(a)
        # d = datetime.now()
        # s = str(d)
        # print(s[0:10])
        #
        # a = load_DSK_today()
        # print(a)
        # b = load_chi_tiet_DSK_today(a[0][0])
        # print(b)
        # print(b[0][2])
        # c = load_users_by_user_id(b[0][2])
        # print(c)

        # pk_today_for_one_user = load_phieu_kham_today_by_user_id(1)
        # user_id_in_phieu_kham = pk_today_for_one_user[0][5]
        # user_in_phieu_kham = load_users_by_user_id(user_id_in_phieu_kham)
        # print(user_in_phieu_kham[0][1])
        # print("\nPhiếu khám\n")
        # print(load_phieu_kham(1))

        # # print(load_role_by_current_user_id())
        #
        # user_id = 1  # Lấy id user bằng nhập trên web
        # pk_today_for_one_user = load_phieu_kham_today_by_user_id(user_id)  # tìm phiếu khám của user đó
        # if pk_today_for_one_user:
        #     user_id_in_phieu_kham = pk_today_for_one_user[0][5]  # Lấy id của user trong phiếu đó
        #     user_in_phieu_kham = load_users_by_user_id(user_id_in_phieu_kham)  # Lấy user trong phiếu đó
        #     print(user_in_phieu_kham)
        #
        # # print(pk_today_for_one_user[0][0])
        # print(load_thuoc_in_chi_tiet_phieu_kham_today(1))
        # print(load_chi_tiet_danh_sach_kham_today(1))
        # print(load_phieu_kham_today_by_phieu_kham_id(2))
        # print(load_phieu_kham_today_by_phieu_kham_id(1))
        # print(load_lich_su_benh(1))
        #
        # print(load_benh_id_by_ten_benh("Đau bụng")[0][0])
        #
        # print(load_hoa_don_by_phieu_kham_id(5))
        #
        # print("HoaDon.id, PhieuKham.id, User.tenUser, HoaDon.ngayKham, HoaDon.tongTien")
        # print(load_hoa_don())
        #
        # print(load_phieu_kham())
        # print(load_lich_su_benh_in_view(1))
        #
        # user_id = 1  # Lấy id user bằng nhập trên web
        # pk_today_for_one_user = load_phieu_kham_today_by_user_id(user_id)  # tìm phiếu khám của user đó
        # if pk_today_for_one_user:
        #     user_id_in_phieu_kham = pk_today_for_one_user[0][5]  # Lấy id của user trong phiếu đó
        #     print("id nè", user_id_in_phieu_kham)
        #
        # print(load_phieu_kham_id_today_by_phieu_kham_id(1)[0][0])
        #
        # print(load_phieu_kham_id_today_by_phieu_kham_id(1))
        # print(load_users_by_user_id(1))
        #
        # print(load_thuoc_in_chi_tiet_phieu_kham_today(1)[0][0])
        # print(load_hoa_don_by_phieu_kham_id(1)[0])
        #
        # print(load_lich_su_benh_in_view(10))

        # print(count_user_in_danh_sach_kham_today()[0][0])
        # print(load_hoa_don())
        # print(load_hoa_don_by_phieu_kham_id(5))
        # a = load_hoa_don_by_phieu_kham_id(5)
        # print(len(a))

        print(count_user_in_register())
        print(load_users_in_register())

