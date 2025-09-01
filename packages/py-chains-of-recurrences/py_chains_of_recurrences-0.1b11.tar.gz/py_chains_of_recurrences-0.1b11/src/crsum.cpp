#include "crsum.hpp"
#include "crnum.hpp"
#include "crexpr.hpp"
#include "crprod.hpp"
#include "crtrig.hpp"

CRsum::CRsum(long long i, size_t l)
{
    index = i;
    length = l;
    operands.resize(length);
    auxiliary.resize(length);
}

CRsum::CRsum(long long i, double x, double h)
{
    length = 2;
    index = i;
    operands.reserve(2);
    operands.push_back(std::make_unique<CRnum>(x));
    operands.push_back(std::make_unique<CRnum>(h));
}

std::unique_ptr<CRobj> CRsum::copy() const
{
    auto result = std::make_unique<CRsum>(index, length);
    for (size_t i = 0; i < length; i++)
    {
        result->operands[i] = operands[i]->copy();
    }
    if (initialized)
    {
        result->initialized = true;
        result->fastvalues.resize(length);
        result->isnumbers.resize(length);

        for (size_t i = 0; i < length; i++)
        {
            result->fastvalues[i] = fastvalues[i];
            result->isnumbers[i] = isnumbers[i];
        }
        result->isanumber.resize(isanumber.size());
        for (size_t i = 0; i < isanumber.size(); i++)
        {
            result->isanumber[i] = isanumber[i];
        }
    }
    return result;
}

// always assume invariant
std::unique_ptr<CRobj> CRsum::add(const CRobj &target) const
{
    if (target.index != index)
    {
        auto result = copy();
        std::unique_ptr<CRobj> temp = nullptr;
        if (operands[0]->index > target.index)
        {
            temp = operands[0]->add(target);
        }
        else
        {
            temp = target.add(*operands[0]);
        }
        // std::cout<<"Finished adding\n";
        result->operands[0] = std::move(temp);
        // std::cout<<"Finished moving\n";
        result->simplify();
        // std::cout<<"Finished simplifying\n";
        return result;
    }
    else if (auto p = dynamic_cast<const CRsum *>(&target))
    {
        size_t maxLen = std::max(length, p->length);
        auto result = std::make_unique<CRsum>(index, maxLen);
        for (size_t i = 0; i < maxLen; ++i)
        {
            double a = (i < length) ? this->operands[i]->valueof() : 0.0;
            double b = (i < target.length) ? p->operands[i]->valueof() : 0.0;
            result->operands[i] = std::make_unique<CRnum>(a + b);
        }
        result->simplify();
        return result;
    }
    else
    {
        return std::make_unique<CRexpr>(oc::ADD, *this->copy(), *target.copy());
    }
}

// TODO: CONSULT JAVA MCR FOR INDEX BLOCK
std::unique_ptr<CRobj> CRsum::mul(const CRobj &target) const
{

    if (target.index != index)
    {
        auto result = copy();
        std::unique_ptr<CRobj> temp = nullptr;
        for (size_t i = 0; i < length; i++)
        {
            if (operands[i]->index > target.index)
            {
                temp = operands[i]->mul(target);
            }
            else
            {
                temp = target.mul(*operands[i]);
            }
            result->operands[i] = std::move(temp);
        }
        result->simplify();
        return result;
    }
    else if (auto p = dynamic_cast<const CRsum *>(&target))
    {  
        //std::cout<<"called here 0"<<"\n";
        
        std::unique_ptr<CRobj> r1 = std::make_unique<CRnum>(0);   
        if (length >= target.length){
            size_t newlength = length + target.length - 1;

            auto result = std::make_unique<CRsum>(index, newlength);
            std::unique_ptr<CRobj> rtemp2 = std::make_unique<CRnum>(0);
            std::unique_ptr<CRobj> r1 = std::make_unique<CRnum>(0);
            std::unique_ptr<CRobj> r2 = std::make_unique<CRnum>(0); 
            std::unique_ptr<CRobj> rtemp1, rtemp11;
            size_t n = length - 1;
            size_t m = target.length - 1;
            for (size_t i = 0; i < newlength; i++){ 
                //std::cout<<"called here 1"<<"\n";
                r1 = std::make_unique<CRnum>(0);
                size_t ibound11 = (i > m ? i - m : 0);
                size_t ibound12 = std::min(i, n);
                for (size_t j = ibound11; j < ibound12 + 1; j++){
                    //std::cout<<"called here 2"<<"\n";
                    r2 = std::make_unique<CRnum>(0);
                    size_t ibound21 = (i > j ? i - j : 0);
                    size_t ibound22 = std::min(i, m);
                    for (size_t k = ibound21; k < ibound22 + 1; k++){
                        //std::cout<<"called here 3"<<"\n";
                        rtemp1 = std::make_unique<CRnum>(choose(j, i - k));
                        rtemp11 = target.operands[k]->copy();
                        //std::cout<<"called here 3.5"<<"\n";
                        rtemp1 = rtemp11->mul(*rtemp1);
                        //std::cout<<"0"<<"\n";
                        if (rtemp1->index > r2->index){
                            r2 = rtemp1->add(*r2); 
                        } else { 
                            r2 = r2->add(*rtemp1);
                        }
                    }
                    rtemp2 = std::make_unique<CRnum>(choose(i, j));
                    r2 = r2->mul(*rtemp2);
                    if (r2->index > operands[j]->index){
                        //std::cout<<"1"<<"\n";
                        rtemp2 = r2->mul(*operands[j]);
                    } else {
                        //std::cout<<"2"<<"\n";
                        rtemp2 = operands[j]->mul(*r2);
                        
                    }
                    if (r1->index > rtemp2->index){
                        //std::cout<<"3"<<"\n";
                        r1 = r1->add(*rtemp2);
                        
                    } else {
                        //std::cout<<"4"<<"\n";
                        r1 = rtemp2->add(*r1);
                    }
                    result->operands[i] = r1->copy();
                    
                }
            }
            result->length = newlength;
            result->simplify();
            return result;
        }   else
        {
            return target.mul(*this);
        }
        // if (length >= target.length)
        // {
        //     size_t newlength = length + target.length - 1;
        //     auto result = std::make_unique<CRsum>(index, newlength);
        //     double rtemp2, r1;
        //     size_t n = length - 1;
        //     size_t m = target.length - 1;
        //     for (size_t i = 0; i < newlength; i++)
        //     {
        //         double r1 = 0;
        //         size_t ibound11 = (i > m ? i - m : 0);
        //         size_t ibound12 = std::min(i, n);
        //         for (size_t j = ibound11; j < ibound12 + 1; j++)
        //         {
        //             double r2 = 0;
        //             size_t ibound21 = (i > j ? i - j : 0);
        //             size_t ibound22 = std::min(i, m);
        //             for (size_t k = ibound21; k < ibound22 + 1; k++)
        //             {
        //                 double rtemp1 = choose(j, i - k);
        //                 // FIX HERE:
        //                 std::unique_ptr<CRobj> rtemp11 = target.operands[k]->copy();
        //                 rtemp1 *= rtemp11;
        //                 r2 += rtemp1;
        //             }
        //             double rtemp2 = choose(i, j);
        //             r2 *= rtemp2;
        //             r2 *= this->operands[j]->valueof();
        //             r1 += r2;
        //         }
        //         result->operands[i] = std::make_unique<CRnum>(r1);
        //     }
        //     result->length = newlength;
        //     result->simplify();
        //     return result;
        // }
        
    }
    else
    {
        return std::make_unique<CRexpr>(oc::MUL, *this->copy(), *target.copy());
    }
}

std::unique_ptr<CRobj> CRsum::pow(const CRobj &target) const
{

    if (auto p = dynamic_cast<const CRnum *>(&target))
    {
        std::unique_ptr<CRobj> result = std::make_unique<CRnum>(1.0);
        double pv = p->valueof();
        if (pv >= 0 && std::floor(pv) == pv)
        {
            size_t exp = size_t(pv);

            std::unique_ptr<CRobj> base = copy();
            while (exp > 0)
            {

                if (exp & 1)
                {
                    if (result->index > base->index)
                    {
                        result = std::move(result->mul(*base));
                    }
                    else
                    {
                        result = std::move(base->mul(*result));
                    }
                }
                exp >>= 1;
                if (exp)
                {
                    base = std::move(base->mul(*base));
                }
            }
            return result;
        }
        else
        {
            return std::make_unique<CRexpr>(oc::POW, *this->copy(), *target.copy());
        }
    }
    else
    {
        return std::make_unique<CRexpr>(oc::POW, *this->copy(), *target.copy());
    }
}

std::unique_ptr<CRobj> CRsum::exp() const
{
    auto result = std::make_unique<CRprod>(index, length);
    for (size_t i = 0; i < length; i++)
    {
        result->operands[i] = std::make_unique<CRnum>(std::exp(operands[i]->valueof()));
    }
    result->simplify();
    return result;
}

std::unique_ptr<CRobj> CRsum::ln() const
{
    return std::make_unique<CRexpr>(oc::LN, *this->copy());
}

std::unique_ptr<CRobj> CRsum::sin() const
{
    auto result = std::make_unique<CRtrig>(index, oc::SIN, length * 2);
    for (size_t i = 0; i < length; i++)
    {
        result->operands[i] = std::make_unique<CRnum>(std::sin(operands[i]->valueof()));
        result->operands[i + length] = std::make_unique<CRnum>(std::cos(operands[i]->valueof()));
    }
    return result;
}

std::unique_ptr<CRobj> CRsum::cos() const
{
    auto result = std::make_unique<CRtrig>(index, oc::COS, length * 2);
    for (size_t i = 0; i < length; i++)
    {
        result->operands[i] = std::make_unique<CRnum>(std::sin(operands[i]->valueof()));
        result->operands[i + length] = std::make_unique<CRnum>(std::cos(operands[i]->valueof()));
    }
    return result;
}

void CRsum::simplify()
{
    return;

    if (operands.empty())
    {
        return;
    }
    size_t j = operands.size() - 1;
    while (j > 0)
    {
        const CRnum *p = dynamic_cast<const CRnum *>(operands[j].get());
        if (p && operands[j]->valueof() == 0)
        {
            j--;
        }
        else
        {
            break;
        }
    }
    if (operands.size() != j + 1)
    {
        operands.resize(j + 1);
    }
    length = operands.size();
}

void CRsum::print_tree() const
{
    std::cout << "CRsum" << "[" << valueof() << "]" << "(";
    for (size_t i = 0; i < operands.size(); i++)
    {
        operands[i]->print_tree();
        if (i + 1 < operands.size())
        {
            std::cout << ", ";
        }
    }
    std::cout << ")";
}

std::string CRsum::genCode(size_t parent, long long order, long long place, std::string indent) const
{
    std::string res;
    std::cout<<order<<" "<<index<<std::endl;
    if (order != index)
    {
        for (size_t i = 0; i < operands.size(); ++i)
        {
            if (!operands[i]->isnumber())
            {
                res += operands[i]->genCode(crposition, order, i, indent);
            }
        }
    }
    else
    {
        size_t n = operands.size();
        // loop header
        res += indent + "for i in range(" + std::to_string(n - 1) + "):\n";
        // sum operation
        res += indent + "    " + crprefix + std::to_string(crposition) + "[i]+=" + crprefix + std::to_string(crposition) + "[i+1]\n";
    }

    if (place != -1 && !res.empty())
    {
        res += indent + crprefix + std::to_string(parent) + "[" + std::to_string(place) + "]=" + crprefix + std::to_string(crposition) + "[0]\n";
    }
    fprintf(stderr, "[genCode:%s] len=%zu lines=%zu\n",
        typeid(*this).name(), res.size(),
        std::count(res.begin(), res.end(), '\n'));
    return res;
}

// can be called without initializing
