// �����������ֻ��ʾ����ҳ�棬�ű�����ժ�� Hengؼԭ���ġ�
function handle(path) {
    // ��ҳ
    if (path == '/zh') {
    alert("box");
        document.getElementsByClassName('radio-inline')[1].click();
        document.getElementById('oneway_from').value='���� (CAN)';
        document.getElementById('oneway_to').value='��¡�� (KUL)';
        document.getElementById('oneway_departuredate').value='2018��9��10��';
        document.getElementsByClassName('btn--booking')[1].click();
        return;
    }

    // ѡ�񺽰�
    if (path == '/Book/Flight') {
        document.getElementsByClassName('price--sale')[0].click();
        document.getElementsByClassName('heading-4')[0].click();
        document.getElementsByClassName('btn-submit')[0].click();
        return;
    }

    // �˿���Ϣ
    if (path == '/BookFlight/Passengers') {
        document.getElementsByClassName('fname1')[0].value = "����";
    }
}
handle(location.pathname);
alert("hello world")