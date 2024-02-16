var updateBtns = document.getElementsByClassName('update-cart')

for(i=0; updateBtns.length; i++)
{
    console.log(i)
    updateBtns[i].addEventListener('click',function(){
        var productid = this.dataset.product
        var action = this.dataset.action
        //console.log(productid, "từ user:",user)
        if(user === "AnonymousUser")
        {
            console.log("a")
        }
        else
        {
            UpdateUserOrder(productid,action)
        }
    })
}


function UpdateUserOrder(productid,action)
{
    var url ="/update_item/"
    fetch(url,{
        method: 'POST',
        headers: {
            'Content-Type':'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({'productId':productid,'action':action})
    })
    .then((response)=>{
        return response.json()
    }
    )
    .then((data)=>{
        console.log('data',data)
        location.reload()
    }
    )
}