(ns feedback.core
  (:require
   [somnium.congomongo :as m]
   [clojure.string :as s]))

(defn connect []
  (let [conn (m/make-connection "lipservice"
                                :host "localhost"
                                :port 27017)]
    (m/set-connection! conn)))

(defn get-result [query id]
  (let [results (filter #(= id (:id %))
                        (get-in query [:response :body :results]))]
    (if (= 1 (count results))
      (first results)
      (println (format "Not 1 result for id %s: %s" id results)))))

(def cols [:type
           :task
           :query
           :document
           :relevant
           :user
           :timestamp
           :url
           :title
           :score])

(defn convert [event query]
  (let [result (get-result query (:id event))]
    {:type "binary"
     :task "teflon-feedback"
     :query (get-in query [:params :text])
     :document (:id event)
     :relevant ({"rated-good" true
                 "rated-bad" false
                 "clicked" nil} (:event event))
     :user (:who query)
     :timestamp (.getTime (:when query))
     :url (:url result)
     :title (:title result)
     :score (:score result)}))

(defn load-data []
  (m/fetch :feedback
           :where {:feedback {:$exists true}}))

(defn process-data [queries]
  (for [query queries
        event (:feedback query)]
    (convert event query)))

(defn escape [s]
  (-> s
      (str)
      (s/replace #"[\t\n]" " ")
      #_(#(if (re-find #"\"" %)
          (format "\"%s\""
                  (s/replace % #"\"" "\"\""))
          %))))

(defn save-data [results fname]
  (with-open [f (clojure.java.io/writer fname)]
    (.write f (str (s/join "\t"
                           (map (comp (partial apply str) rest str)
                                cols))
                   "\n"))
    (doseq [r results]
      (.write f (str (s/join "\t"
                             (map (comp escape r) cols))
                     "\n")))))

(defn -main []
  (connect)
  (let [q (load-data)
        r (process-data q)
        s (filter #(not (nil? (:relevant %))) r)]
    (println "Total " (m/fetch-count :feedback))
    (println "With feedback " (count q))
    (println "Feedbacks " (count r))
    (println "Thumbs" (count s))
    (save-data r "results.txt")
    (save-data s "results2.txt")))
