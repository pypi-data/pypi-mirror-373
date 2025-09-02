import json

from isrpa.Template_Exception import *


def action_message(page, message="等待用户操作", button_label="确认", button=True, time=180):
    """
        参数:
        - page: Page - Playwright的页面对象
        - message: 提示文字
        - button_label: 按钮显示的文字
        - button: 按钮是否显示
        - time: 等待时间(秒)
        """

    js_code = f"""
    (function() {{
        var message = {json.dumps(message)};
        var button = {json.dumps(button)};
        var buttonLabel = {json.dumps(button_label)};
        var time = {time};

        // 创建消息容器
        var msgContainer = document.createElement('div');
        msgContainer.id = 'action-message-container';
        msgContainer.style.position = 'absolute';
        msgContainer.style.right = '20px';
        msgContainer.style.bottom = '20px';
        msgContainer.style.zIndex = '2147483647';
        msgContainer.style.fontFamily = '"Helvetica Neue", Helvetica, Arial, sans-serif';
        msgContainer.style.cursor = 'move'; 
        msgContainer.style.minWidth = '280px'; 
        msgContainer.style.maxWidth = '280px';  

        // 消息框主体
        var messageDiv = document.createElement('div');
        messageDiv.id = 'custom-message';
        messageDiv.style.backgroundColor = 'rgba(255, 255, 255, 0.8)';
        messageDiv.style.color = '#333333';
        messageDiv.style.padding = '16px';
        messageDiv.style.borderRadius = '8px';
        messageDiv.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.15)';
        messageDiv.style.border = '1px solid #eee';
        messageDiv.style.textAlign = 'center';  // 修改为居中对齐

        // 文字内容
        var textDiv = document.createElement('div');
        textDiv.style.lineHeight = '1.5';
        textDiv.style.marginBottom = '12px';
        textDiv.style.textAlign = 'center';  // 添加居中对齐
        textDiv.innerHTML = message;
        messageDiv.appendChild(textDiv);

        // 按钮容器
        var actionDiv = document.createElement('div');
        actionDiv.style.display = 'flex';
        actionDiv.style.gap = '8px';
        actionDiv.style.justifyContent = 'center';

        // 倒计时显示
        var countdownDiv = null;
        if (time > 0) {{
            countdownDiv = document.createElement('div');
            countdownDiv.style.color = '#666';
            countdownDiv.style.fontSize = '12px';
            countdownDiv.style.marginBottom = '8px';
            countdownDiv.innerHTML = `剩余时间：<span style="color:#007bff">${{time}}</span>秒` ;
            messageDiv.insertBefore(countdownDiv, messageDiv.firstChild);
        }}

        // 操作按钮
        if (button) {{
            var btn = document.createElement('button');
            btn.innerHTML = buttonLabel;
            btn.style.backgroundColor = '#007bff';
            btn.style.color = 'white';
            btn.style.border = 'none';
            btn.style.borderRadius = '4px';
            btn.style.padding = '8px 16px';
            btn.style.cursor = 'pointer';
            btn.style.transition = 'all 0.2s';
            btn.style.fontSize = '14px';
            btn.style.fontWeight = 'bold';
            btn.style.boxShadow = '0 2px 4px rgba(0, 0, 0, 0.1)';

            btn.onmouseover = function() {{ this.style.opacity = '0.9' }}; 
            btn.onmouseout = function() {{ this.style.opacity = '1' }};

            btn.onclick = function() {{
                msgContainer.remove();
                window.customButtonClicked = true;
            }};
            actionDiv.appendChild(btn);
        }}

        // 倒计时逻辑
        if (time > 0) {{
            var countdownTime = time;
            var countdownInterval = setInterval(function() {{
                countdownTime--;
                countdownDiv.innerHTML = `剩余时间：<span style="color:#007bff">${{countdownTime}}</span>秒`;
                if (countdownTime <= 0) {{
                    clearInterval(countdownInterval);
                    msgContainer.remove();
                    window.customButtonClicked = true;
                }}
            }}, 1000);
        }}

        // 拖动功能
        var offsetX, offsetY;
        messageDiv.onmousedown = function(e) {{
            offsetX = e.clientX - msgContainer.offsetLeft;
            offsetY = e.clientY - msgContainer.offsetTop;
            document.onmousemove = function(e) {{
                msgContainer.style.left = (e.clientX - offsetX) + 'px';
                msgContainer.style.top = (e.clientY - offsetY) + 'px';
            }};
            document.onmouseup = function() {{
                document.onmousemove = null;
                document.onmouseup = null;
            }};
        }};

        // 监听页面跳转或刷新时，设置 window.customButtonClicked 为 true
        window.addEventListener('beforeunload', function() {{
            window.customButtonClicked = true;
        }});

        // 组合元素
        messageDiv.appendChild(actionDiv);
        msgContainer.appendChild(messageDiv);
        document.body.appendChild(msgContainer);
        window.customButtonClicked = false;
    }})();
    """
    page.wait_for_load_state("domcontentloaded")
    page.evaluate(js_code)
    try:
        page.wait_for_function("window.customButtonClicked === true", timeout=time * 1000)
    except Exception:
        raise Timeout


def info_message(page, current_action="当前执行", message="网页操作"):
    js_code = f"""
    (function() {{
        var currentAction = {json.dumps(current_action)};
        var message = {json.dumps(message)};

        // 创建消息容器
        var msgContainer = document.createElement('div');
        msgContainer.id = 'info-message-container';
        msgContainer.style.position = 'absolute'; 
        msgContainer.style.right = '20px';
        msgContainer.style.top = '20px';
        msgContainer.style.zIndex = '2147483646';
        msgContainer.style.fontFamily = '"Helvetica Neue", Helvetica, Arial, sans-serif';
        msgContainer.style.cursor = 'move';

        // 消息框主体
        var messageDiv = document.createElement('div');
        messageDiv.id = 'info-message';
        messageDiv.style.backgroundColor = 'rgba(255, 255, 255, 0.8)';
        messageDiv.style.color = '#333333';
        messageDiv.style.padding = '16px';
        messageDiv.style.borderRadius = '8px';
        messageDiv.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.15)';
        messageDiv.style.minWidth = '280px';
        messageDiv.style.maxWidth = '280px';
        messageDiv.style.border = '1px solid #eee';
        messageDiv.style.textAlign = 'center';  // 修改为居中对齐

        // 当前执行操作内容
        var currentActionDiv = document.createElement('div');
        currentActionDiv.style.fontWeight = 'bold';
        currentActionDiv.style.color = '#007bff';
        currentActionDiv.style.marginBottom = '8px';
        currentActionDiv.innerHTML = currentAction;
        messageDiv.appendChild(currentActionDiv);

        // 文字内容
        var textDiv = document.createElement('div');
        textDiv.style.lineHeight = '1.5';
        textDiv.style.textAlign = 'center';  // 添加居中对齐
        textDiv.innerHTML = message;
        messageDiv.appendChild(textDiv);

        // 移除现有的 info-message 弹窗
        var existingMessage = document.getElementById('info-message');
        if (existingMessage) {{
            existingMessage.parentElement.remove();
        }}

        // 拖动功能
        var offsetX, offsetY;
        messageDiv.onmousedown = function(e) {{
            offsetX = e.clientX - msgContainer.offsetLeft;
            offsetY = e.clientY - msgContainer.offsetTop;
            document.onmousemove = function(e) {{
                msgContainer.style.left = (e.clientX - offsetX) + 'px';
                msgContainer.style.top = (e.clientY - offsetY) + 'px';
            }};
            document.onmouseup = function() {{
                document.onmousemove = null;
                document.onmouseup = null;
            }};
        }};

        // 组合元素
        msgContainer.appendChild(messageDiv);
        document.body.appendChild(msgContainer);
    }})();
    """
    page.wait_for_load_state("domcontentloaded")
    page.evaluate(js_code)


def info_message2(page, current_action="当前执行", message="网页操作"):
    """
    参数:
    - page: Page - Playwright的页面对象
    - current_action: str - 第一行显示的文字
    - message: str - 第二行显示的文字
    """

    js_code = f"""
    (function() {{
        var line1 = {json.dumps(current_action)};
        var line2 = {json.dumps(message)};
        // 移除现有的 lyrics-message 弹窗
        var existingMessage = document.getElementById('lyrics-message');
        if (existingMessage) {{
            existingMessage.parentElement.remove();
        }}

        // 创建字幕
        var msgContainer = document.createElement('div');
        msgContainer.id = 'lyrics-message-container';
        msgContainer.style.position = 'absolute';  // 使用absolute定位
        msgContainer.style.left = '50%';  // 水平居中
        msgContainer.style.bottom = '20px';  // 显示在页面底部
        msgContainer.style.transform = 'translateX(-50%)';  // 水平居中
        msgContainer.style.zIndex = '2147483647';  // 设置最上层
        msgContainer.style.fontFamily = '"Helvetica Neue", Helvetica, Arial, sans-serif';
        msgContainer.style.pointerEvents = 'none';  // 防止影响页面操作

        // 创建消息框主体
        var messageDiv = document.createElement('div');
        messageDiv.id = 'lyrics-message';
        messageDiv.style.backgroundColor = 'transparent';  // 设置背景透明
        messageDiv.style.color = '#ffffff';
        messageDiv.style.padding = '8px 16px';
        messageDiv.style.borderRadius = '8px';
        messageDiv.style.textAlign = 'center';

        // 第一行文字，使用蓝色
        var textDiv1 = document.createElement('div');
        textDiv1.style.fontSize = '20px';
        textDiv1.style.fontWeight = 'bold';
        textDiv1.style.marginBottom = '4px';
        textDiv1.style.color = '#4a90e2';  // 第一行字体颜色为蓝色
        textDiv1.innerHTML = line1;
        messageDiv.appendChild(textDiv1);

        // 第二行文字，使用深灰色
        var textDiv2 = document.createElement('div');
        textDiv2.style.fontSize = '18px';
        textDiv2.style.lineHeight = '1.5';
        textDiv2.style.color = '#7f8c8d';  // 第二行字体颜色为深灰色
        textDiv2.innerHTML = line2;
        messageDiv.appendChild(textDiv2);

        // 组合元素并添加到页面
        msgContainer.appendChild(messageDiv);
        document.body.appendChild(msgContainer);
    }})();
    """

    # 等待页面加载完成
    page.wait_for_load_state("domcontentloaded")
    # 执行 JS 代码
    page.evaluate(js_code)
