window.onload = function(){
    // for fast loading
    saveSetting(true);
    get_balance();
    get_bid();

    var balance_interval = setInterval(get_balance, 10000);
    var table_interval = setInterval(get_bid, 10000);
    var history_interval = setInterval(get_history, 5000);
};

function get_history() {
    $.get('/history', function(res){
        res = JSON.parse(res);
        $('table.history tbody').empty();
        for(h in res){
            his = res[h];
            $tr = $('table.history tbody').append('<tr>');
            $tr.append(`<td>${his.buy}</td><td>${his.sell}</td><td>${his.cur}</td><td>${his.amount}</td>`)
        }
    });
}

function get_balance(){
    $.get('/exchangekrw/', function(res){
        $('.accs tbody').empty();
        res = JSON.parse(res);
        currencies = [];
        for( cen in res ){
            $('.'+cen + ' .balance_number').text(parseInt(res[cen].get2));

            for( r in res[cen] ){
                if( r != 'get2' && currencies.indexOf(r) == -1 ){
                    currencies.push(r);
                }
            }
        }

        for( cur in currencies ){
            val = 0;
            for( cen in res ){
                if( res[cen][currencies[cur]] ) {
                    val = val + parseFloat(res[cen][currencies[cur]]);
                }
            }
            if( cur == 'krw') {
                $('.accs td.' + currencies[cur]).text(val);
            }
			else if( val == 0 ){
				continue;
			}
            else{
                $('.accs tbody').append(`<tr><td>${currencies[cur]}</td><td>${val.toString().substring(0, 15)}</td></tr>`);
            }
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
            $tr.append(`<td>${cur}</td>`);
            for( c in global_cen ){
                $tr.append(`<td class="${global_cen[c]}"></td>`)
            }
            $tr.append(`<td class="per"></td>`);
            var min = 9999999999;
            var max = 0;
            for(cen in res[cur]){
                if( min > parseInt(res[cur][cen]) ) min = parseInt(res[cur][cen]);
                if( max < parseInt(res[cur][cen]) ) max = parseInt(res[cur][cen]);
                $(`td.${cen}`, $tr).last().text(res[cur][cen]);
            }
            $('td', $tr).last().text(((max-min)/min*100).toFixed(2));
            $(`td:contains(${max})`, $tr).css('background-color', 'aliceblue');
            $(`td:contains(${min})`, $tr).css('background-color', 'lavenderblush');
        }
    });
}

function saveSetting(arg){
    $.get('/save', {alarm: $('.alarm input').is(':checked'),
        trade: $('.trade input').is(':checked'),
        label: $('.label input').val(),
        threshold: $('.trade_thres input').val(),
        alarm_thres: $('.alarm_thres input').val(),
        order: $('.order input').val()}, function(){
        if( !arg )
            alert('저장이 완료되었습니다');
    });
}
