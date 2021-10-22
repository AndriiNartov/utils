let inputField = document.querySelector('#tax_id')
    if (inputField.value) {
        companyList = inputField.value.split(',')
        newValue = `${companyList[companyList.length-1]}, ${companyList[0]}, ${companyList[1]}, ${companyList[2]}`
        inputField.value = newValue
    }
    let companyCreatorPk = inputField.dataset.creator
    let xhttp = new XMLHttpRequest()
    let selectCompanyDiv = document.getElementById("result")

    function clearResContentAndBorder() {
        selectCompanyDiv.innerHTML = ''
        selectCompanyDiv.style.border = 'none'
    }
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            createSelectCompanyDiv(JSON.parse(this.responseText))
        }
    }

    function createSelectCompanyDiv(data) {
        clearResContentAndBorder()
        let list = document.createElement('ul')
        selectCompanyDiv.appendChild(list)
        if (data.queryset.length > 0) {
        for (company of data.queryset) {
            let list_item = document.createElement('li')
            list_item.id = 'company_list_item'
            list_item.innerHTML = `NIP: ${company.tax_id}, ${company.name}, ${company.address.zip_code}, ${company.address.city_name}, ${company.address.street_name}, ${company.address.house_number}`
            list.appendChild(list_item)
        }
        let companyListItems = document.querySelectorAll('#company_list_item')
        companyListItems.forEach(listItem => listItem.addEventListener('click', () => {
                inputField.value = listItem.innerHTML
                clearResContentAndBorder()
            }
            )
        )
        } else {
            let list_item = document.createElement('li')
            list_item.id = 'empty_list_item'
            list_item.innerHTML = 'Нет результатов'
            list.appendChild(list_item)
        }
        if (selectCompanyDiv.innerHTML){
            selectCompanyDiv.style.border = '1px solid black'
        }
    }
    inputField.addEventListener('keyup', () => {
        let tax_id = inputField.value
        if (tax_id && Number(tax_id)){
            xhttp.open('GET', `http://127.0.0.1:8000/debit_note/note/create/ajax/?tax_id=${tax_id}&company_creator=${companyCreatorPk}`, true)
            xhttp.send()
        } else {
            clearResContentAndBorder()
        }
    })