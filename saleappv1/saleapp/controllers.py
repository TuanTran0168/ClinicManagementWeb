from flask import render_template, request, redirect, session, jsonify
from saleapp import app, dao, utils
from flask_login import login_user, logout_user
from saleapp.decorator import annonynous_user
import cloudinary.uploader


def index():
    products = dao.load_products(danhMucThuoc_id=request.args.get('danhMucThuoc_id'),
                                 kw=request.args.get('keyword'))
    return render_template('index.html', Thuoc=products)


def details(product_id):
    p = dao.get_product_by_id(product_id)
    return render_template('details.html', product=p)


def login_admin():
    username = request.form['username']
    password = request.form['password']

    user = dao.auth_user(username=username, password=password)
    if user:
        login_user(user=user)

    return redirect('/admin')


@annonynous_user
def login_my_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = dao.auth_user(username=username, password=password)
        if user:
            login_user(user=user)

            n = request.args.get('next')
            return redirect(n if n else '/')

    return render_template('login.html')


def logout_my_user():
    logout_user()
    return redirect('/login')


# def register():
#     err_msg = ''
#     if request.method == 'POST':
#         name = request.form['name']
#         username = request.form['username']
#         password = request.form['password']  # name cua html
#         confirm = request.form['confirm']
#
#         birthday = request.form['birthday']
#         gender = request.form['sex']
#         telephone = request.form['telephone']
#         address = request.form['address']
#
#         # return gender
#
#         if password.__eq__(confirm):
#             avatar = ''
#             if request.files:
#                 res = cloudinary.uploader.upload(request.files['avatar'])
#                 avatar = res['secure_url']
#
#             try:
#                 dao.register(name=name, username=username, password=password, birthday=birthday, gender=int(gender),
#                              telephone=telephone, address=address, avatar=avatar)
#
#                 return redirect('/login')
#             except:
#                 err_msg = 'Đã có lỗi xảy ra! Vui lòng quay lại sau!'
#         else:
#             err_msg = 'Mật khẩu KHÔNG khớp!'
#
#     return render_template('register.html', err_msg=err_msg)

def register():
    err_msg = ''
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']  # name cua html
        confirm = request.form['confirm']

        birthday = request.form['birthday']
        gender = request.form['sex']
        telephone = request.form['telephone']
        address = request.form['address']

        # return gender

        if password.__eq__(confirm):
            avatar = ''
            if request.files:
                res = cloudinary.uploader.upload(request.files['avatar'])
                avatar = res['secure_url']

            try:
                danh_sach_user = dao.load_users_in_register()
                # return str(danh_sach_user[0][2])
                so_luong_user = dao.count_user_in_register()[0][0]

                for i in range(0, int(so_luong_user)):
                    if str(danh_sach_user[i][2]).__eq__(username):
                        err_msg = "Tên đăng nhập đã tồn tại"
                        return render_template('register.html', err_msg=err_msg)
                else:
                    dao.register(name=name, username=username, password=password, birthday=birthday, gender=int(gender),
                                 telephone=telephone, address=address, avatar=avatar)

                    return redirect('/login')
            except:
                err_msg = 'Đã có lỗi xảy ra! Vui lòng quay lại sau!'
        else:
            err_msg = 'Mật khẩu KHÔNG khớp!'

    return render_template('register.html', err_msg=err_msg)


def cart():
    return render_template('cart.html')


def add_to_cart():
    data = request.json

    key = app.config['CART_KEY']
    cart = session[key] if key in session else {}

    id = str(data['id'])
    name = data['name']
    price = data['price']

    if id in cart:
        cart[id]['quantity'] += 1
    else:
        cart[id] = {
            "id": id,
            "name": name,
            "price": price,
            "quantity": 1
        }

    session[key] = cart

    return jsonify(utils.cart_stats(cart))


def update_cart(product_id):
    key = app.config['CART_KEY']

    cart = session.get(key)
    if cart and product_id in cart:
        cart[product_id]['quantity'] = int(request.json['quantity'])

    session[key] = cart

    return jsonify(utils.cart_stats(cart))


def delete_cart(product_id):
    key = app.config['CART_KEY']

    cart = session.get(key)
    if cart and product_id in cart:
        del cart[product_id]

    session[key] = cart

    return jsonify(utils.cart_stats(cart))


def pay():
    key = app.config['CART_KEY']
    cart = session.get(key)

    try:
        dao.add_receipt(cart=cart)
    except:
        return jsonify({'status': 500})
    else:
        del session[key]
        return jsonify({'status': 200})


def comments(product_id):
    data = []
    for c in dao.load_comments(product_id):
        data.append({
            "id": c.id,
            "content": c.content,
            "created_date": str(c.created_date),
            "user": {
                "name": c.user.name,
                "avatar": c.user.avatar
            }
        })

    return jsonify(data)


def add_comment(product_id):
    try:
        c = dao.save_comment(product_id=product_id, content=request.json['content'])
    except:
        return jsonify({'status': 500})
    else:
        return jsonify({
            'status': 204,
            'comment': {
                "id": c.id,
                "content": c.content,
                "created_date": str(c.created_date),
                "user": {
                    "name": c.user.name,
                    "avatar": c.user.avatar
                }
            }
        })
