
//底部footer显示控制
const footer = document.getElementById('footer');
document.addEventListener('scroll', function() {
    const scrollY = window.scrollY;
    const windowHeight = window.innerHeight;
    const documentHeight = document.body.scrollHeight;
    if (scrollY + windowHeight >= documentHeight) {
        footer.classList.add('show'); // 显示footer
    } else {
        footer.classList.remove('show'); // 隐藏footer
    }
});
//初始是否显示 底部footer
window.onload = function() {
    if (document.body.scrollHeight <= window.innerHeight) {
        footer.classList.add('show'); // 显示footer
    }
};