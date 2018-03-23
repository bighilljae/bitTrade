window.onload = function(){
    // for fast loading
    saveSetting(true);
    get_balance();
    get_bid();

    var balance_interval = setInterval(get_balance, 10000);
    var table_interval = setInterval(get_bid, 10000);
};

function get_balance(){
    $.get('/exchangekrw/', function(res){
        res = JSON.parse(res);
        for( cen in res ){
            $('.'+cen + ' .balance_number').text(parseInt(res[cen]));
        }
    });
}

function get_bid(){
    $.get('/bid/', function(res){
        res = JSON.parse(res);
        var i = 1;
        $('table.contents tbody').empty();
        for(cur in res){
            $tr = $('table.contents tbody').append('<tr>');
            $tr.append(`<td>${cur}</td><td class="korbit"></td><td class="coinone"></td><td class="bithumb"></td><td class="cpdax"></td><td class="per"></td>`);
            var min = 9999999999;
            var max = 0;
            for(cen in res[cur]){
                if( min > parseInt(res[cur][cen]) ) min = parseInt(res[cur][cen]);
                if( max < parseInt(res[cur][cen]) ) max = parseInt(res[cur][cen]);
                $(`td.${cen}`, $tr).last().text(res[cur][cen]);
            }
            $('td', $tr).last().text(((max-min)/min*100).toFixed(2));
        }
    });
}

function saveSetting(arg){
    $.get('/save', {alarm: $('.alarm input').is(':checked'),
        trade: $('.trade input').is(':checked'),
        label: $('.label input').val(),
        threshod: $('.trade_thres input').val()}, function(){
        if( !arg )
            alert('저장이 완료되었습니다');
    });
}