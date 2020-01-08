

package main 

import (
	"net/http"
	"io/ioutil"
	"encoding/json"
	"os"
	"github.com/fsnotify/fsnotify"
)


const url string = "http://127.0.0.1:5000/"

/*


*/


	
type File struct {
	Name string `json:"Name"`
	Path string `json:"Path"`
	AccesTime string `json:"Acces time"`
	ChangeTime string `json:"Change time"`
	Size int `json:"Size"`
}


func check(e error){
	if e != nil{
		panic(e)
	}
}


func getFile(file File) error {

	_file := url + file.Path + file.Name


	resp,err := http.Get(_file)
	defer resp.Body.Close()

	check(err)

	//Creando un nuevo archivo en la ruta indicada
	f,err  := os.Create(string(file.Name))
	check(err)
	defer f.Close()


	body, err := ioutil.ReadAll(resp.Body)
	check(err)


	f.Write(body)
	f.Sync()
	
	return err

}

func getData(){

	resp, err := http.Get(url) 
	defer resp.Body.Close()
	body, err := ioutil.ReadAll(resp.Body)

	check(err)

	f, err := os.Create("data.json")
	check(err)
	defer f.Close()
	f.Write(body)
	f.Sync()

}


func main(){


	//Si archivo ya existe and no hay actualizaciones del server, 
	//no llamar a la función
	//getData()


	data,err := ioutil.ReadFile("data.json")

	if err != nil{
		
		//obteniendo la lista json del servidor
		getData()

		data,err := ioutil.ReadFile("data.json")
		check(err)
	}

	//check(err)

	var files []File

	err = json.Unmarshal(data, &files)


	for i:= 0; i < len(files); i++{
		getFile(files[i])
	} 


}