

package main 

import (
	"net/http"
	"io/ioutil"
	"encoding/json"
	"fmt"
	"os"
)
	
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

func getData(){

	resp, err := http.Get("http://127.0.0.1:5000/") 
	defer resp.Body.Close()
	body, err := ioutil.ReadAll(resp.Body)

	check(err)

	f, err := os.Create("data.json")
	check(err)
	defer f.Close()
	f.Write(body)
	f.Sync()


	fmt.Printf(string(body))
	//ioutil.WriteFile("data.json",body,0777)
	//log.Println(string(body))

}


func main(){

	getData()
	data,err := ioutil.ReadFile("data.json")



	check(err)

	var files []File

	err = json.Unmarshal(data, &files)
	fmt.Printf("files: %+v",files)
}