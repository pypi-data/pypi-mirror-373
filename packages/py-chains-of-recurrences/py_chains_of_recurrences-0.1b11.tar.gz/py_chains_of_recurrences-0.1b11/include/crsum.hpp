#pragma once
#include "crobj.hpp"


class CRsum final: public CRobj {
    public: 
        CRsum(long long i, size_t l); 
        CRsum(long long i, double x, double h);
        
        std::unique_ptr<CRobj> add(const CRobj& target) const override;
        std::unique_ptr<CRobj> mul(const CRobj& target) const override;

        // handle negative power in the visitor
        std::unique_ptr<CRobj> pow(const CRobj& target) const  override;

        //covariant
        std::unique_ptr<CRobj> exp() const override;
        std::unique_ptr<CRobj> ln() const override;

        std::unique_ptr<CRobj> sin() const override;
        std::unique_ptr<CRobj> cos() const override;
        void print_tree() const override;
        void simplify() override;
        
        std::string genCode(size_t parent, long long index, long long place,std::string indent) const override;
        
        std::unique_ptr<CRobj> copy() const override;

        inline void shift(long long i ) noexcept override final {
            //std::cout<<"my index is: "<<index<< " the shifted index is "<<i<<"\n";
            if (index > i){ 
                for (size_t j = 0; j < isanumber.size(); j++){ 
                    operands[isanumber[j]]->shift(i);
                    fastvalues[isanumber[j]] = operands[isanumber[j]]->valueof();
                }
                return;
            } else {
                for (size_t j = 0; j < operands.size()-1; j++){ 
                    fastvalues[j] += fastvalues[j+1];
                }
            }

            // const double* __restrict src = fastvalues.data();
            // double* __restrict dst = auxiliary.data();
            // size_t j = 0;
            // const size_t n = operands.size() -1;
            // for (; j < n; j++){
            //     dst[j] = src[j] + src[j+1];
            // }
            // dst[n] = src[n];
            // fastvalues.swap(auxiliary);
        }

};