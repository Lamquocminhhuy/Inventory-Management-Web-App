
function generatePDF() {
    var billName = document.querySelector('.billName');
    html2canvas(document.querySelector('.container'), {height: document.querySelector('.container').clientHeight, width: document.querySelector('.container').clientWidth}).then(function (canvas) {
        var wid;
        var hgt;

        var img = canvas.toDataURL("image/png", wid = canvas.width, hgt = canvas.height);
        var hratio = hgt / wid
        var doc = new jsPDF('p', 'pt', 'a4');
        var width = doc.internal.pageSize.width;
        var height = width * hratio
        doc.addImage(img, 'JPEG', 0, 0, width, height);
        doc.save(`${billName.innerHTML}.pdf`);
    });
}